from application.dto import UserLogAndPassDTO

from infrastructure.database.models import Users

from presentation.dep_funcs.dependencies import (
    generate_google_oauth_redirect_uri,
    get_http_client,
    access_to_db_session,
    access_to_redis_pipe,
    DepForBindingInnerLayerSQLAlchemy,
)

import uuid
import bcrypt
import aiohttp
import os
from typing import Annotated, cast, Awaitable
from dotenv import load_dotenv
import jwt

from fastapi import HTTPException, Response, Depends, Body, APIRouter, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from redis.asyncio.client import Pipeline


load_dotenv()

auth_router = APIRouter(prefix="/api/auth", tags=["auth"])


@auth_router.post("/registration")
async def registration(
    creds: UserLogAndPassDTO, session: AsyncSession = Depends(access_to_db_session)
) -> dict:

    # Вообще все исключения я пишу в роутах, однако в юз кейсе add_user исключение
    # Рейзится в sql-репозитории, почему? Потому что переделывать уже запарно.
    use_case_add_user = await DepForBindingInnerLayerSQLAlchemy(
        session
    ).add_user_use_case()
    await use_case_add_user(creds.login, creds.password)

    return {"message": "You have successfully registered"}


"""
-----!!!ОЧЕНЬ ВАЖНО!!!--------------------------------------------------------------------------------------------------
Дальше очевидно нужно было бы всё переписать на лад Clean Architecture, однако, 
нужно будет менять или создавать новые функции в интерфейсе, возможно менять entities и тд, в общем это довольно долго,
поэтому код ниже, остаётся не изменённым.
"""


@auth_router.post("/login")
async def login(
    creds: UserLogAndPassDTO,
    request: Request,
    response: Response,
    session: AsyncSession = Depends(access_to_db_session),
    pipe: Pipeline = Depends(access_to_redis_pipe),
) -> dict:

    stmt_for_check = (
        select(Users.id, Users.login, Users.password)
        .where(Users.login == creds.login)
        .limit(1)
    )
    result = await session.execute(stmt_for_check)
    dict_of_result_logpass = result.mappings().first()

    if not dict_of_result_logpass:
        return {"message": "User does not exist"}

    if not bcrypt.checkpw(
        creds.password.encode(), dict_of_result_logpass["password"].encode()
    ):
        raise HTTPException(
            status_code=403, detail="Authentication failed: Неправильный пароль"
        )

    session_id = str(uuid.uuid4())

    await cast(
        Awaitable[int],
        pipe.hsetex(
            f"users:session:{session_id}",
            ex=request.app.state.ttl_auth,
            mapping={"UserId": dict_of_result_logpass.id},
        ),
    )
    await pipe.execute()

    response.set_cookie("session_id", str(session_id), httponly=True)

    return {"message": "User authenticated", "login": creds.login}


@auth_router.get("/google/url")
async def get_google_oauth_redirect_uri(
    uri=Depends(generate_google_oauth_redirect_uri),
):
    return RedirectResponse(url=uri, status_code=302)


@auth_router.post("/google/callback")
async def handle_code(
    code: Annotated[str, Body(embed=True)],
    request: Request,
    response: Response,
    http_client: aiohttp.ClientSession = Depends(get_http_client),
    session: AsyncSession = Depends(access_to_db_session),
    pipe: Pipeline = Depends(access_to_redis_pipe),
) -> dict:

    google_token_url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": os.getenv("OAUTH_GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("OAUTH_GOOGLE_CLIENT_SECRET"),
        "grant_type": "authorization_code",
        "redirect_uri": "http://127.0.0.1:5500/auth.html",
        "code": code,
    }

    try:
        async with http_client.post(
            google_token_url, data=data, ssl=False
        ) as response_google_token:
            if response_google_token.status != 200:
                error_data = await response_google_token.json()
                raise HTTPException(
                    status_code=400,
                    detail=f"Google token exchange failed: {error_data['message']}",
                )
            data_token_google = await response_google_token.json()
    except aiohttp.ClientError as e:
        raise HTTPException(
            status_code=502, detail=f"Failed to connect to Google: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    id_token = data_token_google.get("id_token")
    if not id_token:
        raise HTTPException(
            status_code=400, detail="Missing id_token in Google response"
        )

    data_of_google_user = jwt.decode(
        id_token, algorithms=["RS256"], options={"verify_signature": False}
    )

    google_users_email = data_of_google_user.get("email")

    stmt_for_check = select(Users).where(Users.login == google_users_email).limit(1)
    res = await session.execute(stmt_for_check)
    user = res.scalar_one_or_none()

    if not user:
        try:
            stmt_for_add = insert(Users).values(login=google_users_email, password="")

            await session.execute(stmt_for_add)
            await session.commit()
        except IntegrityError as e:
            await session.rollback()
            raise HTTPException(
                status_code=409, detail=f"Пользователь уже существует\nПодробнее: {e}"
            )

        stmt_for_user_id = (
            select(Users).where(Users.login == google_users_email).limit(1)
        )
        res = await session.execute(stmt_for_user_id)
        user = res.scalar_one_or_none()

    session_id = str(uuid.uuid4())

    await cast(
        Awaitable[int],
        pipe.hsetex(
            f"users:session:{session_id}",
            ex=request.app.state.ttl_auth,
            mapping={
                "UserId": user.id  # type: ignore[union-attr]
            },
        ),
    )
    await pipe.execute()

    response.set_cookie("session_id", str(session_id), httponly=True)

    return {"message": "User authenticated with Google", "login": google_users_email}

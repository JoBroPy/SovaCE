FROM python:3.12-alpine

RUN apk add --no-cache \
    postgresql-dev \
    gcc \
    musl-dev

WORKDIR /app

ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "cd src && uvicorn presentation.main:app --reload --host 0.0.0.0 --port 8000"]
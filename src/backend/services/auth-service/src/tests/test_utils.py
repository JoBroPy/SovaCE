from presentation.dep_funcs.dependencies import generate_google_oauth_redirect_uri

from urllib.parse import urlparse


def test_return_generate_google_oauth_redirect_uri() -> None:
    uri = generate_google_oauth_redirect_uri()
    parsed_uri = urlparse(uri)

    identity_parsed_uri = parsed_uri.scheme in ("http", "https") and bool(
        parsed_uri.netloc
    )

    assert identity_parsed_uri is True

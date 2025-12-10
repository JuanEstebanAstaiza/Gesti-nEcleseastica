from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)


def test_password_hash_and_verify():
    plain = "supersecret"
    hashed = get_password_hash(plain)
    assert hashed != plain
    assert verify_password(plain, hashed)


def test_access_and_refresh_token_scopes():
    access = create_access_token("123")
    refresh = create_refresh_token("123")

    access_payload = decode_token(access)
    refresh_payload = decode_token(refresh)

    assert access_payload["sub"] == "123"
    assert access_payload["scope"] == "access_token"

    assert refresh_payload["sub"] == "123"
    assert refresh_payload["scope"] == "refresh_token"


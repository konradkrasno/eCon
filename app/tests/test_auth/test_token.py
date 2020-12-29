from app.auth.token import get_confirmation_token, verify_token


def test_token():
    token = get_confirmation_token(_id=1, text="test_text")
    token = verify_token(token)
    _id = token.get("_id", None)
    text = token.get("text", None)
    assert _id == 1
    assert text == "test_text"

    token = get_confirmation_token(_id=5)
    token = verify_token(token)
    _id = token.get("_id", None)
    assert _id == 5

    token = verify_token(b"wrong_token")
    _id = token.get("_id", None)
    assert not _id

    token = verify_token(b"wrong_token")
    _id = token.get("_id", None)
    text = token.get("text", None)
    assert not _id
    assert not text

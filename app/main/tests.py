import pytest


def test_index(client, captured_templates):
    response = client.get("/")
    assert response.status_code == 302

from common import client

def test_empty_db(client):
    res = client.get("/")
    assert b"MNGT" in res.data

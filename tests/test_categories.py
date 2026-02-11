def auth_header(client):
    response = client.post(
        "/v1/auth/register",
        json={"email": "cat@example.com", "password": "123456", "name": "Cat"},
    )
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_category(client):
    headers = auth_header(client)
    response = client.post(
        "/v1/categories", json={"name": "Food", "color": "#fff"}, headers=headers
    )
    assert response.status_code == 200
    assert response.json()["data"]["name"] == "Food"

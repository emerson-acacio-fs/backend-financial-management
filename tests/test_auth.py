def test_register_login_me(client):
    register = client.post(
        "/v1/auth/register",
        json={"email": "user@example.com", "password": "123456", "name": "User"},
    )
    assert register.status_code == 200
    token = register.json()["data"]["access_token"]

    login = client.post(
        "/v1/auth/login",
        json={"email": "user@example.com", "password": "123456"},
    )
    assert login.status_code == 200

    me = client.get("/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["data"]["email"] == "user@example.com"

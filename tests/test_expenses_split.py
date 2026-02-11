def auth_header(client):
    response = client.post(
        "/v1/auth/register",
        json={"email": "exp@example.com", "password": "123456", "name": "Exp"},
    )
    token = response.json()["data"]["access_token"]
    user_id = response.json()["data"]["user"]["id"]
    return {"Authorization": f"Bearer {token}"}, user_id


def test_create_expense_valid_split_amount(client):
    headers, user_id = auth_header(client)
    payload = {
        "description": "Dinner",
        "amount": "100.00",
        "currency": "BRL",
        "date": "2026-02-11",
        "split_type": "amount",
        "splits": [
            {"participant_type": "user", "user_id": user_id, "share_amount": "60.00"},
            {"participant_type": "user", "user_id": user_id, "share_amount": "40.00"},
        ],
    }
    response = client.post("/v1/expenses", json=payload, headers=headers)
    assert response.status_code == 200
    assert len(response.json()["data"]["splits"]) == 2


def test_create_expense_invalid_split_amount(client):
    headers, user_id = auth_header(client)
    payload = {
        "description": "Dinner",
        "amount": "100.00",
        "currency": "BRL",
        "date": "2026-02-11",
        "split_type": "amount",
        "splits": [
            {"participant_type": "user", "user_id": user_id, "share_amount": "30.00"},
            {"participant_type": "user", "user_id": user_id, "share_amount": "40.00"},
        ],
    }
    response = client.post("/v1/expenses", json=payload, headers=headers)
    assert response.status_code == 422

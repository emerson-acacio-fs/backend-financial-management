# Finanças compartilhadas — Backend (FastAPI + SQLAlchemy + Postgres)

## Requisitos
- Docker / Docker Compose

## Subir ambiente
```bash
docker compose up -d --build
```

## Migrações
```bash
docker compose exec api alembic upgrade head
```

## Testes e qualidade
```bash
docker compose exec api pytest -q
docker compose exec api ruff check .
docker compose exec api ruff format --check .
```

## Variáveis de ambiente
Copie `.env.example` para `.env` e ajuste conforme necessário:
- `APP_NAME`
- `API_PREFIX`
- `SECRET_KEY`
- `ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `DATABASE_URL`

## Endpoints principais
- `GET /health`
- `POST /v1/auth/register`
- `POST /v1/auth/login`
- `GET /v1/auth/me`
- CRUD completo em `/v1/friends`, `/v1/categories`, `/v1/groups`, `/v1/expenses`

## Exemplos curl
### Register
```bash
curl -X POST http://localhost:8000/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"user@example.com","password":"123456","name":"User"}'
```

### Login
```bash
curl -X POST http://localhost:8000/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"user@example.com","password":"123456"}'
```

### Criar categoria
```bash
curl -X POST http://localhost:8000/v1/categories \
  -H "Authorization: Bearer <TOKEN>" \
  -H 'Content-Type: application/json' \
  -d '{"name":"Alimentação","color":"#22c55e"}'
```

### Criar despesa com split por percentual
```bash
curl -X POST http://localhost:8000/v1/expenses \
  -H "Authorization: Bearer <TOKEN>" \
  -H 'Content-Type: application/json' \
  -d '{
    "description":"Jantar",
    "amount":"100.00",
    "currency":"BRL",
    "date":"2026-02-11",
    "split_type":"percentage",
    "splits":[
      {"participant_type":"user","user_id":"<USER_ID>","share_percentage":"50"},
      {"participant_type":"user","user_id":"<USER_ID>","share_percentage":"50"}
    ]
  }'
```

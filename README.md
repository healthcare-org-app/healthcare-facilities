# facilities-service

facilities-service — domain: identity

- **Port:** 9200
- **Language:** Python 3.11 + Flask
- **Database:** `identity` (Postgres, table `facilities`)
- **Event bus:** Kafka

## API

| Method    | Path                       |
|-----------|----------------------------|
| GET       | `/api/facilities/`          |
| POST      | `/api/facilities/`          |
| GET       | `/api/facilities/<id>`      |
| PUT/PATCH | `/api/facilities/<id>`      |
| DELETE    | `/api/facilities/<id>`      |
| GET       | `/health`                  |
| GET       | `/ready`                   |

## Events

**Publishes:** (none)
**Subscribes:** (none)

## HTTP peer dependencies

- `audit-log-service`

## Local dev

```bash
pip install -e ../../libs/py-healthcare-common
pip install -r requirements.txt
cp .env.example .env
(cd ../../infra && docker compose up -d postgres kafka kafka-init)
python -m app.main
```

## Tests

```bash
pytest
```

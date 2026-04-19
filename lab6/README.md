# Lab 6 — JWT (access + refresh) for books API

## Default demo user

- username: `admin`
- password: `admin`

## Endpoints

- `POST /auth/token` — login, returns `{access_token, refresh_token, token_type}`
  - Uses `application/x-www-form-urlencoded` body: `username`, `password`
- `POST /auth/refresh` — refresh flow with **refresh token rotation**
  - Body JSON: `{ "refresh_token": "..." }`
- `/books*` — protected with `Authorization: Bearer <access_token>`

## Notes

- Access token TTL: 5 minutes (env `ACCESS_TOKEN_TTL_SECONDS`)
- Refresh token TTL: 14 days (env `REFRESH_TOKEN_TTL_SECONDS`)
- Secret: env `JWT_SECRET_KEY` (change in production)


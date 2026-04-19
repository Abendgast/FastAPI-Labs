from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-change-me")
JWT_ALG = os.getenv("JWT_ALG", "HS256")
ACCESS_TOKEN_TTL_SECONDS = int(os.getenv("ACCESS_TOKEN_TTL_SECONDS", "300"))  # 5 min
REFRESH_TOKEN_TTL_SECONDS = int(os.getenv("REFRESH_TOKEN_TTL_SECONDS", "1209600"))  # 14 days

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def _now() -> int:
    return int(time.time())


def _hash_password(password: str) -> str:
    # store as utf-8 string to keep JSON-serializable
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def _verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


def _encode_jwt(payload: dict[str, Any]) -> str:
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALG)


def _decode_jwt(token: str) -> dict[str, Any]:
    return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALG])


@dataclass
class AuthStore:
    # demo users: username -> dict with password_hash
    users: dict[str, dict[str, Any]] = field(default_factory=dict)
    # refresh token rotation: active refresh jti -> record
    refresh_tokens: dict[str, dict[str, Any]] = field(default_factory=dict)

    def ensure_demo_user(self) -> None:
        if "admin" not in self.users:
            self.users["admin"] = {"username": "admin", "password_hash": _hash_password("admin")}

    def authenticate(self, form: OAuth2PasswordRequestForm) -> dict[str, Any] | None:
        self.ensure_demo_user()
        user = self.users.get(form.username)
        if not user:
            return None
        if not _verify_password(form.password, user["password_hash"]):
            return None
        return {"username": user["username"]}

    def issue_token_pair(self, *, username: str) -> tuple[str, str]:
        iat = _now()

        access_payload = {
            "typ": "access",
            "sub": username,
            "iat": iat,
            "exp": iat + ACCESS_TOKEN_TTL_SECONDS,
            "jti": uuid4().hex,
        }
        access = _encode_jwt(access_payload)

        refresh_jti = uuid4().hex
        refresh_payload = {
            "typ": "refresh",
            "sub": username,
            "iat": iat,
            "exp": iat + REFRESH_TOKEN_TTL_SECONDS,
            "jti": refresh_jti,
        }
        refresh = _encode_jwt(refresh_payload)

        self.refresh_tokens[refresh_jti] = {"username": username, "expires_at": refresh_payload["exp"]}
        return access, refresh

    def rotate_refresh(self, *, refresh_token: str) -> tuple[str, str]:
        try:
            payload = _decode_jwt(refresh_token)
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        if payload.get("typ") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        username = payload.get("sub")
        jti = payload.get("jti")
        exp = payload.get("exp")
        if not isinstance(username, str) or not isinstance(jti, str) or not isinstance(exp, int):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        if exp < _now():
            self.refresh_tokens.pop(jti, None)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")

        # rotation: token must be currently active; after use it is revoked
        existing = self.refresh_tokens.pop(jti, None)
        if not existing:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revoked")

        return self.issue_token_pair(username=username)


def get_auth_store() -> AuthStore:
    # module-level singleton (in-memory)
    global _AUTH_STORE  # type: ignore[var-annotated]
    try:
        store = _AUTH_STORE
    except NameError:
        store = AuthStore()
        _AUTH_STORE = store
    return store


def login_and_issue_tokens(
    form: OAuth2PasswordRequestForm = Depends(),
    store: AuthStore = Depends(get_auth_store),
) -> dict[str, Any]:
    user = store.authenticate(form)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access, refresh = store.issue_token_pair(username=user["username"])
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}


def get_current_user(
    token: str = Depends(oauth2_scheme),
) -> dict[str, Any]:
    try:
        payload = _decode_jwt(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.get("typ") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    exp = payload.get("exp")
    username = payload.get("sub")
    if not isinstance(exp, int) or exp < _now() or not isinstance(username, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {"username": username}


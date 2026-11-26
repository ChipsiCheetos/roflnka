import asyncio
import logging
from datetime import UTC, datetime, timedelta

import jwt
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from src.config import settings

SECRET_KEY = settings.JWT_SECRET_KEY.get_secret_value()
ALGORITHM = settings.JWT_ALGORITHM
password_hasher = PasswordHash.recommended()
logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")


class PasswordService:
    async def get_password_hash(self, password: str) -> str:
        return await asyncio.to_thread(password_hasher.hash, password)

    async def verify_password(
        self, plain_password: str, hashed_password: str | None
    ) -> bool:
        if not hashed_password:
            return False
        return await asyncio.to_thread(
            password_hasher.verify, plain_password, hashed_password
        )

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(tz=UTC) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def decode_access_token(self, token: str) -> str | None:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email = payload.get("sub")
            if email is None:
                return None
            return email
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.PyJWTError:
            logger.exception("Invalid token")
            return None

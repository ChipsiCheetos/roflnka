from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from src.auth.schemas import UserCreateSchema, UserResponseSchema
from src.auth.security import PasswordService
from src.database import DbSession
from src.models import User


class UserService:
    def __init__(self, db: DbSession) -> None:
        self.db = db
        self.password_service = PasswordService()

    async def email_search(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()

    async def id_search(self, user_id: UUID) -> User | None:
        statement = select(User).where(User.id == user_id)
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()

    async def register_user(self, user_data: UserCreateSchema) -> UserResponseSchema:
        existing_user = await self.email_search(user_data.email)
        if existing_user is not None:
            raise HTTPException(
                status_code=400, detail="User with this email already exists"
            )
        hashed_password = await self.password_service.get_password_hash(
            user_data.password
        )
        new_user = User(
            email=user_data.email,
            hashed_password=hashed_password,
        )
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return UserResponseSchema.model_validate(new_user)

    async def login_user(self, email: str, password: str) -> str:
        existing_user = await self.email_search(email)
        if existing_user is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        is_valid_password = await self.password_service.verify_password(
            password, existing_user.hashed_password
        )
        if not is_valid_password:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return self.password_service.create_access_token({"sub": email})

    async def get_current_user(self, token: str) -> UserResponseSchema:
        email = self.password_service.decode_access_token(token)
        if email is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user = await self.email_search(email)
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return UserResponseSchema.model_validate(user)

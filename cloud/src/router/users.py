import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from src.auth.schemas import UserCreateSchema, UserResponseSchema
from src.auth.security import oauth2_scheme
from src.database import DbSession
from src.files.user_services import UserService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["Users"])


def get_user_service(db: DbSession) -> UserService:
    return UserService(db)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], user_service: UserServiceDep
) -> UserResponseSchema:
    return await user_service.get_current_user(token)


CurrentUserDep = Annotated[UserResponseSchema, Depends(get_current_user)]


@router.post("/", status_code=201)
async def add_user(
    user_data: UserCreateSchema, user_service: UserServiceDep
) -> UserResponseSchema:
    return await user_service.register_user(user_data)


@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_service: UserServiceDep,
) -> dict[str, str]:
    token = await user_service.login_user(form_data.username, form_data.password)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
async def read_users_me(current_user: CurrentUserDep) -> UserResponseSchema:
    return current_user

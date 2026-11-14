from typing import Annotated
from uuid import UUID

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.auth import (
    AuthTokenResponse,
    StudentLoginRequest,
    StudentRegisterRequest,
    UserSummary,
)

router = APIRouter()
bearer_scheme = HTTPBearer(auto_error=False)


def create_token_response(user: User) -> AuthTokenResponse:
    settings = get_settings()
    return AuthTokenResponse(
        access_token=create_access_token(user.id),
        expires_in=settings.jwt_access_token_minutes * 60,
        user=UserSummary.model_validate(user),
    )


def unauthorized_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password.",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post(
    "/auth/register",
    response_model=AuthTokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_student(
    request: StudentRegisterRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> AuthTokenResponse:
    email = str(request.email).lower()
    existing_user = await session.scalar(select(User).where(User.email == email))
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    user = User(
        email=email,
        display_name=request.display_name,
        password_hash=hash_password(request.password),
        role="student",
    )
    session.add(user)
    try:
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        ) from error

    await session.refresh(user)
    return create_token_response(user)


@router.post("/auth/login", response_model=AuthTokenResponse)
async def login_student(
    request: StudentLoginRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> AuthTokenResponse:
    email = str(request.email).lower()
    user = await session.scalar(select(User).where(User.email == email))
    if user is None or not verify_password(request.password, user.password_hash):
        raise unauthorized_error()
    if not user.is_active or user.role != "student":
        raise unauthorized_error()

    return create_token_response(user)


async def get_current_student(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise unauthorized_error()

    settings = get_settings()
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret_key.get_secret_value(),
            algorithms=["HS256"],
        )
        user_id = UUID(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        raise unauthorized_error() from None

    user = await session.get(User, user_id)
    if user is None or not user.is_active or user.role != "student":
        raise unauthorized_error()
    return user


@router.get("/auth/me", response_model=UserSummary)
async def get_student_profile(
    user: Annotated[User, Depends(get_current_student)],
) -> UserSummary:
    return UserSummary.model_validate(user)

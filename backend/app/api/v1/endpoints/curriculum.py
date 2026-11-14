from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.v1.endpoints.auth import get_current_student
from app.db.session import get_db_session
from app.models.curriculum import Enrollment, Subject, Topic
from app.models.user import User
from app.schemas.curriculum import (
    EnrollmentListResponse,
    EnrollmentResponse,
    SubjectResponse,
)

router = APIRouter(prefix="/catalog")


@router.get("/subjects", response_model=list[SubjectResponse])
async def list_subjects(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[SubjectResponse]:
    result = await session.scalars(
        select(Subject)
        .options(selectinload(Subject.topics).selectinload(Topic.units))
        .order_by(Subject.position)
    )
    return [SubjectResponse.model_validate(subject) for subject in result.all()]


@router.get("/enrollments", response_model=EnrollmentListResponse)
async def list_enrollments(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[User, Depends(get_current_student)],
) -> EnrollmentListResponse:
    result = await session.scalars(
        select(Enrollment)
        .where(Enrollment.user_id == user.id)
        .order_by(Enrollment.enrolled_at)
    )
    return EnrollmentListResponse(
        enrollments=[
            EnrollmentResponse.model_validate(enrollment)
            for enrollment in result.all()
        ]
    )


@router.post(
    "/subjects/{subject_id}/enroll",
    response_model=EnrollmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def enroll_in_subject(
    subject_id: int,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[User, Depends(get_current_student)],
) -> EnrollmentResponse:
    subject = await session.get(Subject, subject_id)
    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning path not found.",
        )

    enrollment = await session.scalar(
        select(Enrollment).where(
            Enrollment.user_id == user.id,
            Enrollment.subject_id == subject_id,
        )
    )
    if enrollment is not None:
        return EnrollmentResponse.model_validate(enrollment)

    enrollment = Enrollment(user_id=user.id, subject_id=subject_id)
    session.add(enrollment)
    try:
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        enrollment = await session.scalar(
            select(Enrollment).where(
                Enrollment.user_id == user.id,
                Enrollment.subject_id == subject_id,
            )
        )
        if enrollment is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Could not enroll in this learning path.",
            ) from error
        return EnrollmentResponse.model_validate(enrollment)

    await session.refresh(enrollment)
    return EnrollmentResponse.model_validate(enrollment)

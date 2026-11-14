from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LearningUnitResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    duration_minutes: int
    video_url: str | None = None
    video_title: str | None = None
    video_source: str | None = None


class TopicResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    video_url: str | None = None
    video_title: str | None = None
    video_source: str | None = None
    units: list[LearningUnitResponse]


class SubjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    title: str
    description: str
    level: str
    pdf_url: str | None = None
    pdf_title: str | None = None
    pdf_source: str | None = None
    pdf_source_url: str | None = None
    pdf_license: str | None = None
    pdf_license_url: str | None = None
    topics: list[TopicResponse]


class EnrollmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    subject_id: int
    enrolled_at: datetime


class EnrollmentListResponse(BaseModel):
    enrollments: list[EnrollmentResponse]

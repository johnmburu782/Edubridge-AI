from typing import Literal

from pydantic import BaseModel


class DashboardStat(BaseModel):
    label: str
    value: str
    icon: Literal["calendar", "target", "file", "briefcase"]


class WeeklyProgressPoint(BaseModel):
    day: str
    score: int


class StudyPlanItem(BaseModel):
    title: str
    time: str
    status: str
    accent: Literal["blue", "violet", "green"]


class OpportunityItem(BaseModel):
    title: str
    detail: str
    priority: str


class DashboardResponse(BaseModel):
    stats: list[DashboardStat]
    weekly_progress: list[WeeklyProgressPoint]
    study_plan: list[StudyPlanItem]
    opportunities: list[OpportunityItem]
    today_checklist: list[str]
    updated_at: str

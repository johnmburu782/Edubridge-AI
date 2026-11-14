"""Create a database-backed demo dashboard snapshot.

Revision ID: 0001_dashboard_snapshot
Revises:
Create Date: 2026-11-14
"""

import json
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001_dashboard_snapshot"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


DEMO_DASHBOARD = {
    "stats": [
        {"label": "Study streak", "value": "18 days", "icon": "calendar"},
        {"label": "Practice score", "value": "92%", "icon": "target"},
        {"label": "Resources saved", "value": "124", "icon": "file"},
        {"label": "Opportunity examples", "value": "7", "icon": "briefcase"},
    ],
    "weekly_progress": [
        {"day": "Mon", "score": 62},
        {"day": "Tue", "score": 68},
        {"day": "Wed", "score": 75},
        {"day": "Thu", "score": 80},
        {"day": "Fri", "score": 86},
        {"day": "Sat", "score": 92},
        {"day": "Sun", "score": 95},
    ],
    "study_plan": [
        {
            "title": "Mathematics",
            "time": "45 min",
            "status": "In progress",
            "accent": "blue",
        },
        {
            "title": "Physics recap",
            "time": "30 min",
            "status": "Next up",
            "accent": "violet",
        },
        {
            "title": "Essay drill",
            "time": "20 min",
            "status": "Ready",
            "accent": "green",
        },
    ],
    "opportunities": [
        {
            "title": "STEM access scholarship (example)",
            "detail": "Demo listing • Eligibility and deadline need verification",
            "priority": "High priority",
        },
        {
            "title": "Data analytics bootcamp (example)",
            "detail": "Demo listing • Program details need verification",
            "priority": "New match",
        },
        {
            "title": "Research internship (example)",
            "detail": "Demo listing • Eligibility details need verification",
            "priority": "Recommended",
        },
    ],
    "today_checklist": [
        "Review algebra mistakes from yesterday",
        "Complete one mock chemistry quiz",
        "Draft application statement for scholarship",
    ],
}


def upgrade() -> None:
    op.create_table(
        "dashboard_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("content", sa.JSON(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    serialized_content = json.dumps(DEMO_DASHBOARD).replace("'", "''")
    op.execute(
        "INSERT INTO dashboard_snapshots (id, content) "
        f"VALUES (1, '{serialized_content}')"
    )


def downgrade() -> None:
    op.drop_table("dashboard_snapshots")

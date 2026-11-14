"""Add Mathematics, Chemistry, and Biology learning paths.

Revision ID: 0003_curriculum_and_enrollments
Revises: 0002_student_accounts
Create Date: 2026-11-14
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0003_curriculum_and_enrollments"
down_revision: Union[str, None] = "0002_student_accounts"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


SUBJECTS = [
    {
        "id": 1,
        "slug": "mathematics",
        "title": "Mathematics",
        "description": "Build confidence with numbers, algebra, geometry, and data.",
        "level": "Foundational",
        "position": 1,
    },
    {
        "id": 2,
        "slug": "chemistry",
        "title": "Chemistry",
        "description": "Explore matter, atoms, bonding, reactions, and acids.",
        "level": "Foundational",
        "position": 2,
    },
    {
        "id": 3,
        "slug": "biology",
        "title": "Biology",
        "description": "Learn about cells, inheritance, body systems, and ecosystems.",
        "level": "Foundational",
        "position": 3,
    },
]

TOPICS = [
    (1, 1, "Numbers and operations", "Work with integers, factors, fractions, and ratios.", 1),
    (2, 1, "Algebra", "Represent patterns and solve introductory equations.", 2),
    (3, 1, "Geometry", "Understand angles, shapes, perimeter, and area.", 3),
    (4, 1, "Data and probability", "Read data displays and reason about chance.", 4),
    (5, 2, "Matter and atoms", "Explore states of matter and atomic structure.", 1),
    (6, 2, "The periodic table", "Organize elements and identify periodic patterns.", 2),
    (7, 2, "Bonding and reactions", "Study chemical bonds and balanced equations.", 3),
    (8, 2, "Acids and bases", "Investigate pH, indicators, and neutralization.", 4),
    (9, 3, "Cell biology", "Learn cell structures and how substances move across membranes.", 1),
    (10, 3, "Genetics", "Explore DNA, genes, and patterns of inheritance.", 2),
    (11, 3, "Human body systems", "Study digestion, nutrition, circulation, and respiration.", 3),
    (12, 3, "Ecology", "Understand food webs, ecosystems, and conservation.", 4),
]

UNITS = [
    (1, 1, "Integers and factors", "Compare integers and identify common factors.", 18, 1),
    (2, 1, "Fractions and ratios", "Compare fractions and solve simple ratio problems.", 20, 2),
    (3, 2, "Expressions and substitution", "Write expressions and evaluate them using given values.", 18, 1),
    (4, 2, "Linear equations", "Solve one-step and two-step linear equations.", 22, 2),
    (5, 3, "Angles and lines", "Recognize angle relationships and use them to find missing angles.", 18, 1),
    (6, 3, "Perimeter and area", "Calculate perimeter and area for common shapes.", 20, 2),
    (7, 4, "Reading charts", "Interpret information from tables and charts.", 16, 1),
    (8, 4, "Basic probability", "Describe the likelihood of simple events.", 18, 2),
    (9, 5, "States of matter", "Compare solids, liquids, and gases.", 18, 1),
    (10, 5, "Atomic structure", "Identify protons, neutrons, and electrons.", 20, 2),
    (11, 6, "Elements and groups", "Use the periodic table to locate elements and groups.", 18, 1),
    (12, 6, "Periodic patterns", "Recognize basic patterns across periods and groups.", 20, 2),
    (13, 7, "Ionic and covalent bonds", "Compare how atoms form ionic and covalent bonds.", 22, 1),
    (14, 7, "Balancing equations", "Balance simple chemical equations.", 22, 2),
    (15, 8, "pH and indicators", "Use the pH scale to classify acids and bases.", 18, 1),
    (16, 8, "Neutralization", "Describe what happens in an acid-base neutralization.", 20, 2),
    (17, 9, "Cell structures", "Identify the main structures in plant and animal cells.", 18, 1),
    (18, 9, "Moving across membranes", "Explore diffusion and osmosis at an introductory level.", 20, 2),
    (19, 10, "DNA and genes", "Connect DNA, genes, and inherited characteristics.", 20, 1),
    (20, 10, "Inheritance patterns", "Read simple inheritance diagrams and family traits.", 22, 2),
    (21, 11, "Digestion and nutrition", "Follow food through the digestive system.", 20, 1),
    (22, 11, "Circulation and respiration", "Describe how oxygen moves through the body.", 22, 2),
    (23, 12, "Food chains and webs", "Trace how energy moves through an ecosystem.", 18, 1),
    (24, 12, "Ecosystems and conservation", "Explore habitats, biodiversity, and conservation.", 20, 2),
]


def upgrade() -> None:
    op.create_table(
        "subjects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("level", sa.String(length=60), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.UniqueConstraint("slug", name=op.f("uq_subjects_slug")),
    )
    op.create_table(
        "topics",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("subject_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["subject_id"],
            ["subjects.id"],
            name=op.f("fk_topics_subject_id_subjects"),
            ondelete="CASCADE",
        ),
    )
    op.create_index("ix_topics_subject_id", "topics", ["subject_id"])
    op.create_table(
        "learning_units",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("topic_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["topic_id"],
            ["topics.id"],
            name=op.f("fk_learning_units_topic_id_topics"),
            ondelete="CASCADE",
        ),
    )
    op.create_index("ix_learning_units_topic_id", "learning_units", ["topic_id"])
    op.create_table(
        "enrollments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("subject_id", sa.Integer(), nullable=False),
        sa.Column(
            "enrolled_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_enrollments_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["subject_id"],
            ["subjects.id"],
            name=op.f("fk_enrollments_subject_id_subjects"),
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "user_id",
            "subject_id",
            name=op.f("uq_enrollments_user_subject"),
        ),
    )
    op.create_index("ix_enrollments_user_id", "enrollments", ["user_id"])

    subjects_table = sa.table(
        "subjects",
        sa.column("id", sa.Integer()),
        sa.column("slug", sa.String()),
        sa.column("title", sa.String()),
        sa.column("description", sa.Text()),
        sa.column("level", sa.String()),
        sa.column("position", sa.Integer()),
    )
    topics_table = sa.table(
        "topics",
        sa.column("id", sa.Integer()),
        sa.column("subject_id", sa.Integer()),
        sa.column("title", sa.String()),
        sa.column("description", sa.Text()),
        sa.column("position", sa.Integer()),
    )
    units_table = sa.table(
        "learning_units",
        sa.column("id", sa.Integer()),
        sa.column("topic_id", sa.Integer()),
        sa.column("title", sa.String()),
        sa.column("description", sa.Text()),
        sa.column("duration_minutes", sa.Integer()),
        sa.column("position", sa.Integer()),
    )
    op.bulk_insert(subjects_table, SUBJECTS)
    op.bulk_insert(
        topics_table,
        [
            {
                "id": topic_id,
                "subject_id": subject_id,
                "title": title,
                "description": description,
                "position": position,
            }
            for topic_id, subject_id, title, description, position in TOPICS
        ],
    )
    op.bulk_insert(
        units_table,
        [
            {
                "id": unit_id,
                "topic_id": topic_id,
                "title": title,
                "description": description,
                "duration_minutes": duration,
                "position": position,
            }
            for unit_id, topic_id, title, description, duration, position in UNITS
        ],
    )


def downgrade() -> None:
    op.drop_index("ix_enrollments_user_id", table_name="enrollments")
    op.drop_table("enrollments")
    op.drop_index("ix_learning_units_topic_id", table_name="learning_units")
    op.drop_table("learning_units")
    op.drop_index("ix_topics_subject_id", table_name="topics")
    op.drop_table("topics")
    op.drop_table("subjects")

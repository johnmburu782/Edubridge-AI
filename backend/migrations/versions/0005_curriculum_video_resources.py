"""Add curated videos to topics and learning units.

Revision ID: 0005_curriculum_video_resources
Revises: 0004_subject_pdf_resources
Create Date: 2026-11-15
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0005_curriculum_video_resources"
down_revision: Union[str, None] = "0004_subject_pdf_resources"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


VIDEO_SOURCE = "Khan Academy"

TOPIC_VIDEOS = [
    (1, "Order of operations with fractions and exponents", "jAVbApE7lJ8"),
    (2, "What are variables, expressions, and equations?", "vDqOoI-4Z6M"),
    (3, "Basic geometry: language and labels", "il0EJrY64qE"),
    (4, "Reading line graphs", "36v2EXZRzUE"),
    (5, "Phase changes", "Aeddl02frBE"),
    (6, "The periodic table", "CtTmUlp3bBo"),
    (7, "Chemical reactions introduction", "TStjgUmL1RQ"),
    (8, "Litmus solution (natural indicator)", "uwfSiFlqt10"),
    (9, "Overview of animal and plant cells", "24YMQ9GvLss"),
    (10, "Chromosomes and genes", "taH5kyoQG0Q"),
    (11, "Organization in the human body", "YE2peDF4Zqg"),
    (12, "Matter and energy in food webs", "qIgL05zOx5U"),
]

UNIT_VIDEOS = [
    (1, "Finding factors of a number", "vcn2ruTOwFo"),
    (2, "Ratios as fractions", "UK-_qEDtvYo"),
    (3, "How to evaluate an expression using substitution", "tC1SfxRvtmM"),
    (4, "Solving two-step equations", "_y_Q3_B2Vh8"),
    (5, "Angle basics", "H-de6Tkxej8"),
    (6, "Perimeter and area: the basics", "LoaBd-sPzkU"),
    (7, "Interpreting two-way tables", "MarqSlyz-lU"),
    (8, "Probability explained", "uzkc-qNVoOk"),
    (9, "States of matter", "We7Kd4D0S90"),
    (10, "Protons, neutrons, and electrons in atoms", "lz_gMkQr7YE"),
    (11, "Groups of the periodic table", "jQGUkJc7_04"),
    (12, "Atomic radii trends", "RrwL99bEotk"),
    (13, "Ionic bonds", "FaeAurHnQJs"),
    (14, "Balancing chemical equations", "TUuABq95BBM"),
    (15, "Acid-base indicators", "ZDgYWaeuwbw"),
    (16, "Acid-base neutralization reaction", "aXs4gS43rko"),
    (17, "Overview of animal and plant cells", "24YMQ9GvLss"),
    (18, "Diffusion and osmosis", "aubZU0iWtgI"),
    (19, "Genes, DNA, and chromosomes", "IdWqsI0DSzE"),
    (20, "Pedigrees", "11s5Biyi9q4"),
    (21, "Human digestive system", "2uL4b1yMhm8"),
    (22, "Transport of oxygen", "8XTnKgW8EKo"),
    (23, "Food chains and food webs", "HRyjMbuMDn0"),
    (24, "Human impacts on ecosystems", "K10qnzCYH54"),
]


def _seed_video_resources(table_name: str, resources: list[tuple[int, str, str]]) -> None:
    connection = op.get_bind()
    for item_id, title, video_id in resources:
        connection.execute(
            sa.text(
                f"""
                UPDATE {table_name}
                SET video_url = :video_url,
                    video_title = :video_title,
                    video_source = :video_source
                WHERE id = :id
                """
            ),
            {
                "id": item_id,
                "video_url": f"https://www.youtube.com/watch?v={video_id}",
                "video_title": title,
                "video_source": VIDEO_SOURCE,
            },
        )


def upgrade() -> None:
    for table_name in ("topics", "learning_units"):
        op.add_column(table_name, sa.Column("video_url", sa.String(length=1000), nullable=True))
        op.add_column(table_name, sa.Column("video_title", sa.String(length=250), nullable=True))
        op.add_column(table_name, sa.Column("video_source", sa.String(length=80), nullable=True))

    _seed_video_resources("topics", TOPIC_VIDEOS)
    _seed_video_resources("learning_units", UNIT_VIDEOS)


def downgrade() -> None:
    for table_name in ("learning_units", "topics"):
        op.drop_column(table_name, "video_source")
        op.drop_column(table_name, "video_title")
        op.drop_column(table_name, "video_url")

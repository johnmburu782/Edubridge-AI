"""Add downloadable open textbook resources to learning subjects.

Revision ID: 0004_subject_pdf_resources
Revises: 0003_curriculum_and_enrollments
Create Date: 2026-11-14
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0004_subject_pdf_resources"
down_revision: Union[str, None] = "0003_curriculum_and_enrollments"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


PDF_RESOURCES = [
    {
        "slug": "mathematics",
        "pdf_url": "https://assets.openstax.org/oscms-prodcms/media/documents/prealgebra-2e_-_WEB.pdf",
        "pdf_title": "Prealgebra 2e",
        "pdf_source": "OpenStax",
        "pdf_source_url": "https://openstax.org/details/books/prealgebra-2e",
        "pdf_license": "CC BY-NC-SA 4.0",
        "pdf_license_url": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
    },
    {
        "slug": "chemistry",
        "pdf_url": "https://assets.openstax.org/oscms-prodcms/media/documents/chemistry-2e_-_WEB.pdf",
        "pdf_title": "Chemistry 2e",
        "pdf_source": "OpenStax",
        "pdf_source_url": "https://openstax.org/details/books/chemistry-2e",
        "pdf_license": "CC BY-NC-SA 4.0",
        "pdf_license_url": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
    },
    {
        "slug": "biology",
        "pdf_url": "https://assets.openstax.org/oscms-prodcms/media/documents/Concepts-Biology_-_WEB.pdf",
        "pdf_title": "Concepts of Biology",
        "pdf_source": "OpenStax",
        "pdf_source_url": "https://openstax.org/details/books/concepts-biology",
        "pdf_license": "CC BY-NC-SA 4.0",
        "pdf_license_url": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
    },
]


def upgrade() -> None:
    op.add_column("subjects", sa.Column("pdf_url", sa.String(length=1000), nullable=True))
    op.add_column("subjects", sa.Column("pdf_title", sa.String(length=160), nullable=True))
    op.add_column("subjects", sa.Column("pdf_source", sa.String(length=80), nullable=True))
    op.add_column("subjects", sa.Column("pdf_source_url", sa.String(length=500), nullable=True))
    op.add_column("subjects", sa.Column("pdf_license", sa.String(length=160), nullable=True))
    op.add_column("subjects", sa.Column("pdf_license_url", sa.String(length=500), nullable=True))

    connection = op.get_bind()
    for resource in PDF_RESOURCES:
        connection.execute(
            sa.text(
                """
                UPDATE subjects
                SET pdf_url = :pdf_url,
                    pdf_title = :pdf_title,
                    pdf_source = :pdf_source,
                    pdf_source_url = :pdf_source_url,
                    pdf_license = :pdf_license,
                    pdf_license_url = :pdf_license_url
                WHERE slug = :slug
                """
            ),
            resource,
        )


def downgrade() -> None:
    op.drop_column("subjects", "pdf_license_url")
    op.drop_column("subjects", "pdf_license")
    op.drop_column("subjects", "pdf_source_url")
    op.drop_column("subjects", "pdf_source")
    op.drop_column("subjects", "pdf_title")
    op.drop_column("subjects", "pdf_url")

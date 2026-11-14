# EduBridge AI

EduBridge AI is a student-first learning and opportunity platform for guided study, exam preparation, educational resources, and verified opportunities. The project is being built incrementally; only the Phase 1 foundation described below is implemented at this stage.

## System architecture

```text
React + Vite browser client
        │ HTTPS / JSON (versioned REST API)
        ▼
FastAPI application ─────── OpenAI API (backend only; optional until AI phase)
        │
        ├── SQLAlchemy async ORM ── PostgreSQL
        ├── Alembic schema migrations
        └── Isolated domain services
              ├── tutoring and recommendations
              ├── PDF extraction, summarization, and document Q&A
              ├── quiz generation and grading
              └── application writing assistance
```

The browser never receives database credentials or the OpenAI key. FastAPI owns authentication, authorization, validation, and all AI-provider calls. PostgreSQL is the source of truth for users, learning activity, and opportunity records. AI and document processing are separated from HTTP handlers so providers and implementations can be replaced without changing the client contract.

## Folder structure

```text
.
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/     # Versioned HTTP endpoints (health check exists)
│   │   ├── core/                 # Runtime configuration and security
│   │   ├── db/                   # SQLAlchemy base and async sessions
│   │   ├── models/               # ORM entities
│   │   ├── schemas/              # Pydantic request/response types
│   │   ├── services/             # AI, PDF, quiz, and application logic
│   │   ├── utils/                # Shared backend utilities
│   │   └── main.py               # FastAPI app
│   ├── migrations/               # Alembic environment and revisions
│   ├── alembic.ini
│   └── requirements.txt
├── src/
│   ├── app/                      # Router and application shell (next UI phase)
│   ├── components/               # Shared accessible UI
│   ├── features/                 # Auth, dashboard, tutor, PDFs, exams, etc.
│   ├── lib/                      # API client and frontend utilities
│   └── styles/                   # Global design tokens and styles
├── docker-compose.yml            # Local PostgreSQL service
├── .env.example                  # Local configuration template; no real keys
└── README.md
```

## Data model plan

All persisted entities use UUID primary keys and UTC creation/update timestamps where appropriate. Foreign keys are indexed; uniqueness and check constraints will be added with their corresponding migrations.

| Entity | Purpose and key relationships |
|---|---|
| `users` | Unique email, password hash, role (`student` / `admin`), active status |
| `student_profiles` | One-to-one user profile, display name, education level, region, preferences |
| `subjects` | Catalog of subjects and topics |
| `learning_resources` | Curated materials; optionally associated with a subject and publishing admin |
| `uploaded_documents` | User-owned PDF metadata, storage key, processing state, extracted-text reference |
| `conversations` | User-owned tutor or document-assistant threads, optional document association |
| `chat_messages` | Ordered conversation turns, role, content, and provider metadata |
| `quizzes` | Subject/topic, creator, generation source, and publication state |
| `questions` | Quiz-owned multiple-choice or short-answer questions and validated answer data |
| `quiz_attempts` | User attempt, score, start/completion timestamps |
| `quiz_answers` | Per-question answer and correctness/explanation snapshot for an attempt |
| `opportunities` | Scholarships, bootcamps, courses, internships; source URL, eligibility, deadline, and verification state |
| `applications` | User-owned application drafts/status linked to an opportunity when applicable |
| `learning_progress` | User/subject/topic progress and completion state |
| `user_activities` | Auditable learning activity events used for analytics |

Opportunity records will distinguish verified sources from unverified submissions. No opportunity details, deadlines, eligibility, or links will be shown as verified without a traceable official source.

## Development roadmap

1. **Project setup and architecture** — complete: frontend toolchain, backend package, configuration, PostgreSQL service, API health endpoint, architecture and schema documentation.
2. **Database and authentication** — ORM models, Alembic baseline, registration/login, password hashing, JWT, role-based access, and auth tests.
3. **Frontend and student dashboard** — responsive design system, routing, dashboard, and authenticated API client.
4. **Core REST APIs** — resources, progress, profiles, and activity APIs with validation and pagination.
5. **AI integration** — modular tutoring, recommendations, quiz, and application services using server-side OpenAI credentials; explicit unavailable-provider behavior and rate limits.
6. **PDF and exam preparation** — restricted PDF uploads, extraction, document-grounded Q&A, quizzes, attempts, and performance tracking.
7. **Opportunity discovery** — search/filter APIs, provenance and verification workflow, and admin publishing.
8. **Analytics and administration** — learner analytics and protected admin management/monitoring.
9. **Testing and hardening** — integration/accessibility/security checks, performance review, and production configuration.
10. **Deployment and documentation** — deployment topology, operational guidance, API documentation, and safe demonstration data.

## Phase 1 setup

### Prerequisites

- Node.js 20.19+ or 22.12+ and npm
- Python 3.11+
- Docker Desktop (or a local PostgreSQL 16 instance)

### Configure and start PostgreSQL

From the repository root in PowerShell:

```powershell
Copy-Item .env.example .env
# Set JWT_SECRET_KEY in .env to a unique random secret before starting the API.
docker compose up -d db
```

The example database credentials are only for local development. Use managed secrets and a dedicated database user outside local development.

### Start the frontend

```powershell
npm install
npm run dev
```

### Start the API and database

```powershell
docker compose up -d db
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Before starting the API, copy `.env.example` to `.env` in the repository root and replace `JWT_SECRET_KEY` with a random value of at least 32 characters. The API reads its configuration from this file.

The Vite development server proxies `/api` requests to `http://localhost:8000`. For a separately hosted API, set `VITE_API_BASE_URL` to its `/api/v1` URL and include the frontend origin in `FRONTEND_ORIGINS`.

Student accounts use `POST /api/v1/auth/register` and `POST /api/v1/auth/login`; both return a bearer token. `GET /api/v1/auth/me` validates the signed-in student. Run `alembic upgrade head` to create the account table before using these endpoints.

The learning catalog is seeded by migration `0003_curriculum_and_enrollments`. `GET /api/v1/catalog/subjects` lists Mathematics, Chemistry, and Biology with their topics and units. Migration `0004_subject_pdf_resources` adds official OpenStax PDF URLs, source details, and license links to those subjects. Migration `0005_curriculum_video_resources` adds Khan Academy video links for each topic and unit; the frontend opens videos on YouTube and does not download or host third-party content. Signed-in students can view their enrollments with `GET /api/v1/catalog/enrollments` and enroll in a subject with `POST /api/v1/catalog/subjects/{subject_id}/enroll`; the enrolled subject card’s **Start learning** button expands its topics and units.

### Run the API without Docker

For local development on a machine without PostgreSQL, the API can use a SQLite database file instead:

```powershell
cd backend
$env:DATABASE_URL = "sqlite+aiosqlite:///./edubridge-dev.db"
$env:JWT_SECRET_KEY = "<unique random value of at least 32 characters>"
alembic upgrade head
uvicorn app.main:app --reload
```

Keep the same `DATABASE_URL` and `JWT_SECRET_KEY` in the API terminal while it is running. SQLite data is local to this development machine; use PostgreSQL for deployment.

The dashboard endpoint (`http://localhost:8000/api/v1/dashboard`) reads the sample dashboard snapshot inserted by the initial Alembic migration. If the API is unreachable, the frontend shows a clearly labeled local demo preview and keeps the connection error visible with a retry action; the preview is not database-backed or personalized. `/api/v1/health` reports API liveness, `/api/v1/health/ready` checks database connectivity, and interactive OpenAPI documentation is at `http://localhost:8000/docs`.

### Current implementation boundary

Student email/password registration and login, and enrollment in the seeded Mathematics, Chemistry, and Biology learning paths, are implemented but require the API and database to be running. The dashboard snapshot is shared demo data and is not personalized. User-specific progress, live opportunity data, AI functionality, and demonstration accounts remain on the roadmap.

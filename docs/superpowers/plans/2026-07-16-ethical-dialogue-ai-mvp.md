# Ethical Dialogue AI MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Docker-runnable full-stack MVP that demonstrates the ethical Telegram lead workflow from simulated message to lead and analytics.

**Architecture:** Use a monorepo with a Django REST backend and Vite React frontend. Keep external integrations behind provider interfaces so local mock Telegram/AI providers and real Vertex/Telegram providers share the same workflow. Prioritize the core consent-first business pipeline over broad marketing/admin polish.

**Tech Stack:** Python, Django, Django REST Framework, Simple JWT, PostgreSQL, Redis, Celery, React, TypeScript, Vite, Tailwind CSS, TanStack Query, React Router, React Hook Form, Zod, Recharts, Docker Compose.

## Global Constraints

- AI provider for production path is platform-managed Google Vertex AI.
- Customer-provided AI credentials are deferred.
- Local MVP must run without paid external services using mock providers.
- Telegram MVP uses a mock provider first, with official Bot API provider behind the same interface.
- Consent-first behavior must be enforced in backend logic.
- Never implement mass messaging, unsolicited outreach lists, random direct messaging, private-contact scraping, or automated broadcast spam.
- Sensitive credentials must not be committed, logged, or copied into documentation.
- Dashboard and ethical workflow come before landing-page polish.
- All tenant-bound backend data must be workspace-scoped.
- Use real backend APIs from the frontend; do not ship a fake-data-only UI.

---

## File Structure

### Root

- Create `.gitignore`: ignore Python/Node artifacts, env files, Docker volumes, media, and local credentials.
- Create `.env.example`: safe environment template for local/mock mode and Vertex setup.
- Create `docker-compose.yml`: local development services.
- Create `Makefile`: common commands for setup, test, lint, seed, and run.
- Create `README.md`: quick start, demo credentials, mock mode, Vertex setup, and known limitations.
- Create `docs/IMPLEMENTATION_STATUS.md`: progress checklist.
- Create `docs/ARCHITECTURE.md`, `docs/LOCAL_SETUP.md`, `docs/AI_PIPELINE.md`, `docs/TELEGRAM_SETUP.md`, `docs/TESTING.md`, `docs/SECURITY.md`, `docs/DEPLOYMENT.md`, `docs/API.md`, `docs/PRODUCT_WORKFLOWS.md`.

### Backend

- Create `backend/manage.py`.
- Create `backend/requirements/base.txt`, `backend/requirements/dev.txt`.
- Create `backend/pytest.ini`.
- Create `backend/config/settings.py`, `backend/config/urls.py`, `backend/config/celery.py`, `backend/config/asgi.py`, `backend/config/wsgi.py`.
- Create `backend/apps/common/`: base models, API errors, permissions, workspace helpers, rate-limit primitives.
- Create `backend/apps/accounts/`: custom user model, auth serializers/views/urls, seed user support.
- Create `backend/apps/workspaces/`: workspace, membership, role permissions.
- Create `backend/apps/products/`: product models/API.
- Create `backend/apps/triggers/`: trigger models, matching service, test endpoint.
- Create `backend/apps/telegram_integration/`: connection/chat/contact/update models, mock provider, simulator endpoint.
- Create `backend/apps/ai_engine/`: provider protocol, mock provider, Vertex provider, schemas, safety service.
- Create `backend/apps/opportunities/`: opportunity, response draft, approval workflow.
- Create `backend/apps/consent/`: consent record and service.
- Create `backend/apps/conversations/`: conversation and message models/API.
- Create `backend/apps/leads/`: lead models/API.
- Create `backend/apps/analytics/`: overview metrics endpoint.
- Create `backend/apps/notifications/`: simple notification model/API.
- Create `backend/apps/audit_logs/`: immutable audit log model/service/API.
- Create `backend/apps/billing/`: plan, subscription, usage models used by seed and usage display.
- Create `backend/apps/demo/management/commands/seed_demo.py`: deterministic demo data.
- Create focused tests in `backend/tests/`.

### Frontend

- Create `frontend/package.json`, `frontend/vite.config.ts`, `frontend/tsconfig.json`, `frontend/tailwind.config.js`, `frontend/postcss.config.js`, `frontend/index.html`.
- Create `frontend/src/main.tsx`, `frontend/src/app/App.tsx`, `frontend/src/app/router.tsx`, `frontend/src/app/queryClient.ts`.
- Create `frontend/src/services/api.ts`: typed fetch client with JWT support.
- Create `frontend/src/features/auth/`: sign-in page and auth state.
- Create `frontend/src/layouts/DashboardLayout.tsx`: workspace dashboard shell.
- Create `frontend/src/components/ui/`: buttons, cards, badges, inputs, tables, empty states.
- Create `frontend/src/pages/`: Overview, Telegram, Simulator, Opportunities, Approvals, Conversations, Leads, Products, Triggers, Analytics, Settings.
- Create `frontend/src/types/api.ts`: shared API response types.
- Create `frontend/src/tests/`: frontend tests for sign-in and workflow UI.

### Infrastructure

- Create `infrastructure/nginx/default.conf`: production-ready reverse proxy skeleton.
- Create `backend/Dockerfile`, `frontend/Dockerfile`, `infrastructure/docker/backend-entrypoint.sh`.

---

## Task 1: Repository Foundation And Local Runtime

**Files:**
- Create: `.gitignore`
- Create: `.env.example`
- Create: `docker-compose.yml`
- Create: `Makefile`
- Create: `backend/Dockerfile`
- Create: `frontend/Dockerfile`
- Create: `infrastructure/docker/backend-entrypoint.sh`
- Create: `infrastructure/nginx/default.conf`
- Modify: `docs/IMPLEMENTATION_STATUS.md`

**Interfaces:**
- Produces: local service names `backend`, `frontend`, `db`, `redis`, `celery`, `celery-beat`.
- Produces env variables used by backend settings: `DJANGO_SECRET_KEY`, `DATABASE_URL`, `REDIS_URL`, `AI_PROVIDER`, `TELEGRAM_PROVIDER`, `VERTEX_PROJECT_ID`, `VERTEX_LOCATION`, `VERTEX_MODEL`.

- [ ] **Step 1: Create runtime files**

Write Docker and environment files that allow `docker compose up --build` to start all services after backend/frontend code exists.

- [ ] **Step 2: Add status checklist**

Create `docs/IMPLEMENTATION_STATUS.md` with unchecked sections for foundation, backend workflow, frontend workflow, tests, docs, and deployment.

- [ ] **Step 3: Verify compose config**

Run: `docker compose config`

Expected: compose YAML renders successfully with services `backend`, `frontend`, `db`, `redis`, `celery`, and `celery-beat`.

- [ ] **Step 4: Commit**

Run:

```bash
git add .gitignore .env.example docker-compose.yml Makefile backend/Dockerfile frontend/Dockerfile infrastructure docs/IMPLEMENTATION_STATUS.md
git commit -m "chore: add local runtime foundation"
```

## Task 2: Django Project, Settings, And Shared API Foundation

**Files:**
- Create: `backend/manage.py`
- Create: `backend/requirements/base.txt`
- Create: `backend/requirements/dev.txt`
- Create: `backend/pytest.ini`
- Create: `backend/config/settings.py`
- Create: `backend/config/urls.py`
- Create: `backend/config/celery.py`
- Create: `backend/config/asgi.py`
- Create: `backend/config/wsgi.py`
- Create: `backend/apps/common/models.py`
- Create: `backend/apps/common/api.py`
- Create: `backend/apps/common/permissions.py`
- Create: `backend/apps/common/workspace.py`

**Interfaces:**
- Produces: `TimestampedModel`, `WorkspaceScopedModel`, `api_success(data, status=200)`, `api_error(code, message, fields=None, status=400)`.
- Produces: DRF/JWT/OpenAPI base routes at `/api/v1/` and `/api/docs/`.

- [ ] **Step 1: Add dependencies**

Use Django, DRF, Simple JWT, django-cors-headers, django-filter, drf-spectacular, psycopg, dj-database-url, Celery, Redis, pytest, pytest-django, factory_boy, ruff, black.

- [ ] **Step 2: Configure Django**

Set custom user model placeholder `accounts.User`, installed apps, REST framework defaults, JWT auth, CORS, database from `DATABASE_URL`, Redis/Celery URLs, static/media settings, and OpenAPI.

- [ ] **Step 3: Add common helpers**

Implement base UUID timestamp models and API error envelope helpers.

- [ ] **Step 4: Verify Django boot**

Run: `cd backend && python manage.py check`

Expected: Django system check passes after app skeletons exist.

- [ ] **Step 5: Commit**

Run:

```bash
git add backend
git commit -m "chore: add Django API foundation"
```

## Task 3: Auth, Workspaces, Roles, And Demo Seed

**Files:**
- Create: `backend/apps/accounts/models.py`
- Create: `backend/apps/accounts/serializers.py`
- Create: `backend/apps/accounts/views.py`
- Create: `backend/apps/accounts/urls.py`
- Create: `backend/apps/accounts/admin.py`
- Create: `backend/apps/workspaces/models.py`
- Create: `backend/apps/workspaces/serializers.py`
- Create: `backend/apps/workspaces/views.py`
- Create: `backend/apps/workspaces/urls.py`
- Create: `backend/apps/workspaces/permissions.py`
- Create: `backend/apps/demo/management/commands/seed_demo.py`
- Test: `backend/tests/test_auth_workspace.py`

**Interfaces:**
- Produces: `User`, `Workspace`, `WorkspaceMembership`.
- Produces roles: `owner`, `admin`, `manager`, `analyst`, `reviewer`.
- Produces endpoints: `POST /api/v1/auth/login/`, `POST /api/v1/auth/refresh/`, `GET /api/v1/auth/me/`, `GET /api/v1/workspaces/`.
- Produces seed credentials documented in README and `.env.example`.

- [ ] **Step 1: Write auth/workspace tests**

Test login, `/me`, workspace listing, and cross-workspace isolation.

- [ ] **Step 2: Implement models and permissions**

Create custom email user, workspace model, membership model, and `IsWorkspaceMember` permission.

- [ ] **Step 3: Implement APIs**

Use Simple JWT token obtain/refresh and custom `/me` response containing user and memberships.

- [ ] **Step 4: Implement seed command**

Create demo owner, manager, analyst, reviewer, one workspace, and memberships.

- [ ] **Step 5: Verify**

Run:

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
python manage.py seed_demo
pytest tests/test_auth_workspace.py -v
```

Expected: migrations apply, seed command is idempotent, tests pass.

- [ ] **Step 6: Commit**

Run:

```bash
git add backend
git commit -m "feat: add auth workspace and demo seed"
```

## Task 4: Domain Models For Workflow

**Files:**
- Create: `backend/apps/products/models.py`
- Create: `backend/apps/triggers/models.py`
- Create: `backend/apps/telegram_integration/models.py`
- Create: `backend/apps/ai_engine/models.py`
- Create: `backend/apps/opportunities/models.py`
- Create: `backend/apps/consent/models.py`
- Create: `backend/apps/conversations/models.py`
- Create: `backend/apps/leads/models.py`
- Create: `backend/apps/analytics/models.py`
- Create: `backend/apps/notifications/models.py`
- Create: `backend/apps/audit_logs/models.py`
- Create: `backend/apps/billing/models.py`
- Modify: `backend/apps/demo/management/commands/seed_demo.py`
- Test: `backend/tests/test_models_seed.py`

**Interfaces:**
- Produces model classes listed in the design spec.
- Produces status enums for opportunities, drafts, consent, leads, messages, and Telegram connections.
- Produces demo product `SalesPilot CRM`, trigger set, mock Telegram connection, mock chat, plan, and subscription.

- [ ] **Step 1: Write seed/model tests**

Test `seed_demo` creates the demo product, trigger, mock connection, chat, plan, and no duplicate records on second run.

- [ ] **Step 2: Implement workflow models**

Add workspace-scoped models with UUID primary keys, timestamps, indexes, and useful constraints.

- [ ] **Step 3: Extend seed command**

Seed realistic product, trigger examples, chat, contacts, initial analytics-friendly records where appropriate.

- [ ] **Step 4: Verify**

Run:

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
python manage.py seed_demo
pytest tests/test_models_seed.py -v
```

Expected: tests pass and seed command remains idempotent.

- [ ] **Step 5: Commit**

Run:

```bash
git add backend
git commit -m "feat: add workflow domain models"
```

## Task 5: AI, Trigger, Safety, And Telegram Provider Services

**Files:**
- Create: `backend/apps/triggers/services.py`
- Create: `backend/apps/ai_engine/schemas.py`
- Create: `backend/apps/ai_engine/providers/base.py`
- Create: `backend/apps/ai_engine/providers/mock.py`
- Create: `backend/apps/ai_engine/providers/vertex.py`
- Create: `backend/apps/ai_engine/services.py`
- Create: `backend/apps/ai_engine/safety.py`
- Create: `backend/apps/telegram_integration/providers/base.py`
- Create: `backend/apps/telegram_integration/providers/mock.py`
- Create: `backend/apps/telegram_integration/services.py`
- Test: `backend/tests/test_ai_trigger_safety.py`

**Interfaces:**
- Produces: `match_trigger_set(message_text, trigger_set) -> TriggerMatchResult`.
- Produces: `AIProvider.classify_message(input)`, `generate_permission_request(input)`, `generate_product_response(input)`.
- Produces: `get_ai_provider()`.
- Produces: `validate_permission_first_response(text, consent_status, product) -> SafetyResult`.
- Produces: `MockTelegramProvider.send_message(...) -> TelegramSendResult`.

- [ ] **Step 1: Write service tests**

Test CRM recommendation trigger matching, negative trigger exclusion, mock AI structured classification, permission draft disclosure, product response blocked before consent, and allowed after consent.

- [ ] **Step 2: Implement trigger service**

Return matched positive/negative terms, numeric score, and reason string.

- [ ] **Step 3: Implement mock AI provider**

Return deterministic structured results for the required CRM demo message and safe fallback for irrelevant messages.

- [ ] **Step 4: Implement Vertex provider shell**

Use Google Cloud Vertex AI SDK only when `AI_PROVIDER=vertex`. Raise clear configuration errors if required env vars or credentials are missing.

- [ ] **Step 5: Implement safety service**

Block promotional product claims when consent is not granted and require AI disclosure for initial permission request.

- [ ] **Step 6: Implement mock Telegram provider**

Persist simulated send status and return deterministic message IDs.

- [ ] **Step 7: Verify**

Run: `cd backend && pytest tests/test_ai_trigger_safety.py -v`

Expected: tests pass.

- [ ] **Step 8: Commit**

Run:

```bash
git add backend
git commit -m "feat: add AI trigger safety and Telegram providers"
```

## Task 6: End-To-End Backend Workflow APIs

**Files:**
- Create: `backend/apps/products/serializers.py`, `views.py`, `urls.py`
- Create: `backend/apps/triggers/serializers.py`, `views.py`, `urls.py`
- Create: `backend/apps/telegram_integration/serializers.py`, `views.py`, `urls.py`
- Create: `backend/apps/opportunities/serializers.py`, `views.py`, `urls.py`, `services.py`
- Create: `backend/apps/consent/serializers.py`, `views.py`, `urls.py`, `services.py`
- Create: `backend/apps/conversations/serializers.py`, `views.py`, `urls.py`, `services.py`
- Create: `backend/apps/leads/serializers.py`, `views.py`, `urls.py`, `services.py`
- Create: `backend/apps/analytics/serializers.py`, `views.py`, `urls.py`
- Create: `backend/apps/notifications/serializers.py`, `views.py`, `urls.py`
- Create: `backend/apps/audit_logs/serializers.py`, `views.py`, `urls.py`, `services.py`
- Modify: `backend/config/urls.py`
- Test: `backend/tests/test_demo_workflow_api.py`

**Interfaces:**
- Produces: simulator endpoint `POST /api/v1/telegram/simulate-message/`.
- Produces: approval endpoint `POST /api/v1/approvals/{draft_id}/approve/`.
- Produces: consent endpoint `POST /api/v1/conversations/{id}/simulate-consent/`.
- Produces: response endpoint `POST /api/v1/conversations/{id}/generate-product-response/`.
- Produces: lead conversion endpoint `POST /api/v1/leads/convert/`.
- Produces: analytics endpoint `GET /api/v1/analytics/overview/`.

- [ ] **Step 1: Write workflow API test**

Test the exact acceptance flow: login, simulate CRM message, assert opportunity/draft, approve draft, simulate consent, generate product response, convert to lead, update lead status, assert analytics counts.

- [ ] **Step 2: Implement workflow orchestration service**

Create one service function that runs ingestion, trigger matching, AI classification, opportunity creation, draft creation, and audit logging in a transaction.

- [ ] **Step 3: Implement CRUD/list APIs**

Add list/detail endpoints needed by frontend for products, triggers, opportunities, approvals, conversations, leads, notifications, audit logs, and analytics.

- [ ] **Step 4: Implement approval and consent APIs**

Ensure approval sends only permission request before consent. Ensure product response generation fails unless consent is granted.

- [ ] **Step 5: Verify**

Run:

```bash
cd backend
pytest tests/test_demo_workflow_api.py -v
python manage.py spectacular --file schema.yml
```

Expected: tests pass and OpenAPI schema generates.

- [ ] **Step 6: Commit**

Run:

```bash
git add backend
git commit -m "feat: add ethical workflow APIs"
```

## Task 7: React App Foundation And Authenticated Dashboard Shell

**Files:**
- Create frontend project files listed in File Structure.
- Create: `frontend/src/services/api.ts`
- Create: `frontend/src/features/auth/AuthProvider.tsx`
- Create: `frontend/src/features/auth/SignInPage.tsx`
- Create: `frontend/src/layouts/DashboardLayout.tsx`
- Create: `frontend/src/components/ui/*`
- Create: `frontend/src/pages/OverviewPage.tsx`
- Test: `frontend/src/tests/auth.test.tsx`

**Interfaces:**
- Consumes: `POST /api/v1/auth/login/`, `GET /api/v1/auth/me/`, `GET /api/v1/analytics/overview/`.
- Produces: protected dashboard route `/app`.

- [ ] **Step 1: Create frontend foundation**

Set up Vite React TypeScript, Tailwind, Router, TanStack Query, and API client.

- [ ] **Step 2: Implement sign-in**

Persist access/refresh tokens in local storage for local MVP and redirect to `/app`.

- [ ] **Step 3: Implement dashboard shell**

Add sidebar navigation, top bar, workspace name, user menu placeholder, and responsive layout.

- [ ] **Step 4: Implement overview**

Show KPI cards from analytics API, setup checklist, health panel, and recent activity.

- [ ] **Step 5: Verify**

Run:

```bash
cd frontend
npm install
npm run build
```

Expected: TypeScript build succeeds.

- [ ] **Step 6: Commit**

Run:

```bash
git add frontend
git commit -m "feat: add authenticated dashboard shell"
```

## Task 8: Frontend Workflow Pages

**Files:**
- Create: `frontend/src/pages/TelegramPage.tsx`
- Create: `frontend/src/pages/SimulatorPage.tsx`
- Create: `frontend/src/pages/OpportunitiesPage.tsx`
- Create: `frontend/src/pages/ApprovalsPage.tsx`
- Create: `frontend/src/pages/ConversationsPage.tsx`
- Create: `frontend/src/pages/LeadsPage.tsx`
- Create: `frontend/src/pages/ProductsPage.tsx`
- Create: `frontend/src/pages/TriggersPage.tsx`
- Create: `frontend/src/pages/AnalyticsPage.tsx`
- Modify: `frontend/src/app/router.tsx`
- Test: `frontend/src/tests/workflow.test.tsx`

**Interfaces:**
- Consumes all MVP workflow endpoints from Task 6.
- Produces complete browser flow for the required demo.

- [ ] **Step 1: Implement Telegram and simulator pages**

Show mock connection, monitored chat, input for sample message, and response with opportunity link.

- [ ] **Step 2: Implement opportunities and approvals**

List opportunities, show draft text, approve/edit/reject actions, and safety/status badges.

- [ ] **Step 3: Implement conversations and consent**

Show message history, consent timeline, simulate consent reply, and generate product response button.

- [ ] **Step 4: Implement leads**

List leads, convert from conversation/opportunity where needed, update status, and show simple pipeline columns.

- [ ] **Step 5: Implement products, triggers, analytics**

Add minimal CRUD/list screens and database-derived charts/metrics.

- [ ] **Step 6: Verify**

Run:

```bash
cd frontend
npm run build
```

Expected: TypeScript build succeeds.

- [ ] **Step 7: Commit**

Run:

```bash
git add frontend
git commit -m "feat: add ethical workflow dashboard pages"
```

## Task 9: End-To-End Verification, Docs, And Production Notes

**Files:**
- Modify: `README.md`
- Modify: `docs/IMPLEMENTATION_STATUS.md`
- Modify: `docs/ARCHITECTURE.md`
- Modify: `docs/LOCAL_SETUP.md`
- Modify: `docs/AI_PIPELINE.md`
- Modify: `docs/TELEGRAM_SETUP.md`
- Modify: `docs/TESTING.md`
- Modify: `docs/SECURITY.md`
- Modify: `docs/DEPLOYMENT.md`
- Modify: `docs/API.md`
- Modify: `docs/PRODUCT_WORKFLOWS.md`
- Create: `backend/tests/test_security_regressions.py`

**Interfaces:**
- Produces: documented local run command, demo credentials, mock behavior, Vertex configuration, deployment path, and known limitations.

- [ ] **Step 1: Add security regression tests**

Test no product response before consent, workspace isolation on key list endpoints, and no token field returned from Telegram connection API.

- [ ] **Step 2: Run backend tests**

Run: `cd backend && pytest -v`

Expected: backend tests pass.

- [ ] **Step 3: Run frontend build**

Run: `cd frontend && npm run build`

Expected: TypeScript build succeeds.

- [ ] **Step 4: Run Docker Compose smoke test**

Run:

```bash
docker compose up --build
```

Expected: backend health endpoint, frontend page, Postgres, Redis, Celery, and seed path work locally.

- [ ] **Step 5: Write docs**

Document exact commands, demo credentials, mock Telegram, mock AI, Vertex AI environment variables, VPS deployment steps, and known limitations.

- [ ] **Step 6: Update status**

Mark completed items in `docs/IMPLEMENTATION_STATUS.md` and list deferred items honestly.

- [ ] **Step 7: Commit**

Run:

```bash
git add README.md docs backend/tests
git commit -m "docs: document MVP setup and verification"
```

## Task 10: VPS Deployment Preparation

**Files:**
- Create: `docker-compose.prod.yml`
- Create: `infrastructure/nginx/prod.conf`
- Create: `infrastructure/scripts/deploy_vps.sh`
- Modify: `docs/DEPLOYMENT.md`

**Interfaces:**
- Consumes: server SSH access supplied out-of-band by the user.
- Produces: repeatable production deployment script that does not embed secrets.

- [ ] **Step 1: Add production compose**

Configure backend, frontend static build or Nginx serving, db, redis, celery, celery-beat, and reverse proxy.

- [ ] **Step 2: Add deploy script**

Create an idempotent script that syncs repository files to the VPS, prompts for env file setup, builds containers, runs migrations, seeds demo data only when requested, and restarts services.

- [ ] **Step 3: Verify script syntax**

Run: `bash -n infrastructure/scripts/deploy_vps.sh`

Expected: no syntax errors.

- [ ] **Step 4: Commit**

Run:

```bash
git add docker-compose.prod.yml infrastructure docs/DEPLOYMENT.md
git commit -m "chore: add VPS deployment preparation"
```

---

## Self-Review

- Spec coverage: the plan covers local MVP runtime, auth/workspaces, domain models, mock Telegram, mock AI plus Vertex provider shell, consent enforcement, workflow APIs, frontend dashboard pages, analytics, tests, documentation, and VPS deployment preparation.
- Intentional gaps: full production billing, full landing polish, real email delivery, complete super-admin, advanced file knowledge ingestion, and BYO AI credentials are deferred as documented in the approved design.
- Placeholder scan: no task relies on undefined future work for the MVP demo. The only deferred items are explicitly outside MVP scope.
- Type consistency: provider names, endpoint paths, model domains, and environment variables match the design spec.

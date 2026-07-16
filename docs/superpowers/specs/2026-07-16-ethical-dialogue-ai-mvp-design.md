# Ethical Dialogue AI MVP Design

Date: 2026-07-16
Status: Approved direction, pending implementation plan

## Goal

Build a production-oriented local MVP for Ethical Dialogue AI: a multi-tenant SaaS that detects relevant needs in authorized Telegram communities, drafts permission-first responses, records consent, and converts interested contacts into leads.

The first implementation must prove the complete ethical workflow end to end without paid external services:

```text
Simulated Telegram message
-> ingestion
-> trigger matching
-> AI classification
-> opportunity creation
-> permission-request draft
-> human approval
-> simulated Telegram send
-> consent recording
-> grounded product response
-> conversation
-> lead creation
-> analytics update
```

Real Telegram and real Vertex AI providers will share the same interfaces as mock providers, so the local MVP can later move to production without rewriting the workflow.

## Scope

### In MVP

- Monorepo with `backend/`, `frontend/`, `infrastructure/`, and `docs/`.
- Docker Compose for Django, React, PostgreSQL, Redis, Celery worker, Celery Beat, and local development services.
- Django REST API with tenant-aware models and permission checks.
- React dashboard-first frontend connected to real backend APIs.
- Demo auth, workspace, roles, products, triggers, opportunities, approval queue, consent, conversations, leads, notifications, and analytics.
- Mock Telegram provider and simulator.
- AI provider abstraction with `MockAIProvider` and platform-managed `VertexAIProvider`.
- Consent-first backend enforcement.
- Audit logs for important decisions and actions.
- Seed data and demo credentials for local development.
- Focused tests for the critical workflow.
- Documentation for local setup, architecture, Telegram setup, AI pipeline, security, testing, and deployment.

### Deferred After MVP

- Full production billing integration.
- Full landing page polish and all marketing/legal routes.
- Real email provider delivery.
- Advanced file-based knowledge ingestion.
- Full super-admin experience.
- BYO customer AI credentials.
- Complete Telegram Business automation if API access or account capability is unavailable during local development.

## Architecture

### Backend

Use Django, Django REST Framework, PostgreSQL, Redis, Celery, Django Channels-ready structure, JWT auth, django-filter, drf-spectacular, and django-cors-headers.

The backend is organized around domain apps:

- `accounts`: users, sessions, JWT integration, auth views.
- `workspaces`: workspaces, memberships, roles, tenant context.
- `telegram_integration`: connections, chats, mock provider, webhook ingestion, simulated updates.
- `products`: product and approved offer data used by AI.
- `triggers`: keyword, phrase, negative, and semantic trigger configuration.
- `ai_engine`: provider interface, mock provider, Vertex provider, output schemas, request logs, safety validation.
- `opportunities`: detected needs, drafts, feedback, approval queue.
- `consent`: consent records and consent timeline.
- `conversations`: messages, conversation state, simulated sends.
- `leads`: lightweight CRM and lead pipeline.
- `analytics`: database-derived metrics.
- `notifications`: in-app notifications and event records.
- `billing`: plans, usage records, mock subscriptions.
- `audit_logs`: immutable audit trail.

Shared backend patterns:

- Service classes own business workflow.
- Serializers validate API input/output.
- Selectors centralize query logic when it reduces duplication.
- Permissions enforce workspace membership and role capabilities.
- Models use UUID primary keys where practical.
- Tenant-bound data includes `workspace_id`.

### Frontend

Use React, TypeScript, Vite, Tailwind CSS, shadcn/ui-style components, React Router, TanStack Query, React Hook Form, Zod, Recharts, and Lucide icons.

The first screen after sign-in is the dashboard, not a marketing shell. The frontend contains:

- Auth pages for sign-in and basic session handling.
- Workspace-aware dashboard layout.
- Overview with KPIs, setup checklist, health panel, and recent activity.
- Telegram page with mock connection status and simulator link.
- AI playground/simulator for sample messages.
- Opportunities list and detail drawer.
- Approval queue with approve/edit/reject actions.
- Conversations page with consent events and message history.
- Leads table and simple pipeline/status update.
- Products and triggers CRUD enough to power the demo flow.
- Analytics page backed by real database counts.

UI should be restrained and operational: dense but readable, with clear tables, filters, badges, drawers, empty states, loading states, and mobile-friendly fallbacks.

## AI Design

The AI layer exposes a provider interface:

```text
class AIProvider:
    classify_message(input) -> ClassificationResult
    generate_permission_request(input) -> DraftResult
    generate_product_response(input) -> DraftResult
```

### Mock Provider

The mock provider returns deterministic structured results for local development and tests. It must handle the required demo message:

```text
Can anyone recommend a simple CRM for a small sales team?
```

Expected behavior:

- classify as relevant;
- intent: recommendation request / CRM need;
- confidence high enough to create an opportunity;
- generate a transparent permission request;
- after consent, generate a grounded product response based on enabled product data.

### Vertex Provider

The real initial AI provider is Google Vertex AI using the platform owner's Google Cloud account.

Environment variables:

- `AI_PROVIDER=vertex`
- `VERTEX_PROJECT_ID`
- `VERTEX_LOCATION`
- `VERTEX_MODEL`
- `GOOGLE_APPLICATION_CREDENTIALS` or equivalent workload identity setup

Customer-provided AI keys are not part of MVP. Workspace usage is still logged per workspace for quota, billing, and audit reporting.

The backend validates model output with strict schemas. It stores concise decision explanations only, never hidden chain-of-thought.

## Telegram Design

Telegram integration uses a provider boundary:

```text
class TelegramProvider:
    validate_connection(...)
    configure_webhook(...)
    send_message(...)
    parse_update(...)
```

### MVP Provider

The first provider is `MockTelegramProvider`, supporting:

- mock connection display;
- simulated inbound messages;
- simulated sent messages;
- deterministic delivery status;
- webhook-like processing through the same backend pipeline.

### Real Provider

The real provider will use official Telegram Bot API webhooks and Telegram Business features where available. Unofficial userbot scraping is not the default architecture.

Real provider implementation must:

- validate webhook secret;
- avoid logging sensitive payloads;
- encrypt bot tokens at rest;
- never return token values in normal API responses;
- enforce authorized chat selection before monitoring.

## Consent And Safety

Consent is enforced in backend workflow, not just frontend copy.

Rules:

- The assistant must disclose itself as an AI or automated business assistant.
- The first outbound response must ask permission before product promotion.
- Promotional content is blocked until consent is granted.
- If consent is denied, the system stops promotional interaction.
- Automation mode defaults to monitoring-only or manual approval.
- Bulk promotional sending is out of scope and should not be implemented.
- Rate limits are checked before AI generation and simulated sending.
- Every automated decision stores an audit-friendly reason.

Safety validation checks generated text for:

- promotion before consent;
- missing AI disclosure;
- unsupported prices or claims;
- forbidden claims;
- aggressive tone;
- unsupported links;
- excessive length;
- personal data leakage.

## Data Flow

1. User signs in with demo credentials.
2. User opens demo workspace.
3. User enters a simulated Telegram message.
4. Backend creates a normalized message record.
5. Rule filters verify chat status, schedule, sender, and limits.
6. Trigger service calculates keyword and negative-trigger matches.
7. AI service classifies the message using mock or Vertex provider.
8. Decision engine creates an opportunity if thresholds pass.
9. AI service creates a permission-request draft.
10. Approval queue stores the draft for human review.
11. Reviewer approves or edits the permission request.
12. Telegram provider simulates sending the permission request.
13. User simulates contact consent.
14. Consent record is created with evidence reference.
15. AI service generates a product response grounded in product/knowledge data.
16. Conversation messages and system events are persisted.
17. User converts conversation/opportunity to a lead.
18. Analytics endpoints return updated counts.

## API Surface

Versioned API prefix: `/api/v1/`.

MVP endpoint groups:

- `auth`: sign in, refresh, logout, me.
- `workspaces`: current workspace, memberships, role summary.
- `products`: list/create/update demo product data.
- `triggers`: list/create/update/test trigger sets.
- `telegram`: mock connection, chats, simulator, webhook logs.
- `ai`: playground and provider status.
- `opportunities`: list/detail, feedback, status updates.
- `approvals`: queue, approve, edit-and-send, reject.
- `conversations`: list/detail, simulate contact reply, generate response.
- `consent`: timeline, grant/deny/withdraw.
- `leads`: list/detail/status/update/convert.
- `analytics`: overview metrics and funnel.
- `notifications`: list, mark read.
- `audit-logs`: list filtered by workspace.

Errors use a consistent envelope:

```json
{
  "error": {
    "code": "validation_error",
    "message": "The request could not be processed.",
    "fields": {}
  }
}
```

## Deployment Path

### Phase 1: Local MVP

Build and verify locally with:

```bash
docker compose up --build
```

The app must work without real Telegram or Vertex credentials by using mock providers.

### Phase 2: VPS Deployment

After the local MVP passes the demo flow, deploy to the provided VPS using:

- Docker Compose production file;
- Nginx reverse proxy;
- Gunicorn for Django HTTP;
- Daphne or ASGI server for websocket-ready traffic;
- Celery worker and beat;
- PostgreSQL and Redis services or managed equivalents;
- environment-managed secrets.

Credentials supplied in chat are operational secrets. They must not be committed, logged, or copied into documentation. They should be rotated after initial setup.

## Testing Strategy

Backend tests:

- auth happy path;
- workspace tenant isolation;
- role permission checks;
- trigger matching;
- duplicate simulated update handling;
- AI schema validation;
- consent enforcement;
- approval workflow;
- lead conversion;
- analytics counts.

Frontend tests:

- sign-in form;
- protected route behavior;
- simulator submit flow;
- opportunity appears after simulation;
- approval action updates queue;
- lead status update.

End-to-end target:

1. Sign in.
2. Open demo workspace.
3. Open Telegram simulator.
4. Submit the CRM recommendation message.
5. See opportunity and draft.
6. Approve permission request.
7. Simulate consent reply.
8. Generate product response.
9. Convert to lead.
10. Update lead status.
11. Confirm analytics changed.

## Success Criteria

The first implementation is acceptable when:

- Docker Compose starts core services.
- Migrations run.
- Seed command creates demo data.
- User can sign in.
- Dashboard pages load from real APIs.
- Simulated Telegram message processing works.
- Trigger matching and AI classification work.
- Opportunity, draft, approval, consent, conversation, and lead records are persisted.
- Analytics are database-derived.
- TypeScript build succeeds.
- Backend tests for the workflow pass.
- README explains local startup, demo credentials, mock mode, Vertex setup, and deployment path.

## Open Decisions Resolved

- AI provider: platform-managed Google Vertex AI.
- Customer AI credentials: deferred.
- First build path: local MVP first, VPS deployment second.
- Telegram: mock provider first, official Bot API provider behind the same interface.
- Main implementation focus: dashboard and ethical workflow before landing-page polish.

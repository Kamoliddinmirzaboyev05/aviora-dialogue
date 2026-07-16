# Ethical Dialogue AI Production Readiness Design

## Goal

Turn the existing MVP into a deployable product with a real Gemini Developer API provider, an official Telegram Bot API integration, a polished public landing page, and a staff-only superadmin console while preserving the current consent-first workflow and mock providers.

## Product Surfaces

The frontend remains one React application with three explicit surfaces:

- `/` is the public landing page. It communicates the product, ethical workflow, key capabilities, and primary sign-in call to action.
- `/app/*` is the authenticated customer workspace dashboard already present in the MVP.
- `/superadmin/*` is a custom staff-only operations console for platform-wide metrics, workspaces, users, integration state, and recent operational failures.

The Django admin remains available at `/admin/` as a low-level maintenance tool. All domain models receive useful list, search, filter, and readonly configuration so it is operationally usable even when the React console is unavailable.

## Visual Direction

The landing page uses a crisp light foundation with deep charcoal text, electric teal, coral, and lime accents. The hero uses a generated bitmap product visual that shows the real consent-first Telegram workflow instead of an abstract stock image. Motion is restrained and functional: hero reveal, workflow rail movement, metric count-up, and intersection-based section entrances. `prefers-reduced-motion` disables nonessential movement.

The first viewport names Ethical Dialogue AI, shows the workflow visual, provides `Start now` and `Sign in` actions, and leaves the next section visible. The page includes workflow, capabilities, trust principles, product preview, and final call-to-action sections. Mobile navigation, keyboard access, focus states, responsive text constraints, and semantic landmarks are required.

The superadmin is dense and operational rather than promotional. It uses a sidebar, compact summary metrics, searchable tables, integration health indicators, and direct links to the Django admin for destructive or low-level edits.

## AI Providers

`get_ai_provider()` supports exactly three configured modes:

- `AI_PROVIDER=mock` returns `MockAIProvider` and requires no external credentials.
- `AI_PROVIDER=gemini` returns `GeminiAPIProvider`, requires `GEMINI_API_KEY`, and uses `GEMINI_MODEL` with a default of `gemini-2.5-flash`.
- `AI_PROVIDER=vertex` returns `VertexAIProvider` and validates the existing Vertex project, location, model, and Google credential configuration.

The Gemini provider uses the official `google-genai` Python SDK. The API key is passed directly to `genai.Client` and is never serialized, logged, returned in an exception message, or stored in the database.

Gemini classification uses structured output with an SDK-supported Pydantic response schema. Provider output is converted into the existing immutable `ClassificationResult` dataclass. Permission and product responses are converted into the existing `DraftResult` dataclass. The provider validates semantic ranges such as confidence and supplies safe error messages when the upstream response is invalid or unavailable.

Django startup checks validate the selected provider only. Gemini mode does not inspect or require any Vertex setting. Mock mode does not require any external secret. Unknown provider names fail clearly instead of silently falling back to mock.

## AI Connection Test

`POST /api/v1/ai/test-connection/` accepts a workspace UUID. Only active workspace owners or admins may call it. It sends a fixed harmless CRM classification sample through the selected provider and returns:

- selected provider name and model label;
- connection state;
- latency in milliseconds;
- the normalized classification result.

The endpoint never accepts an arbitrary prompt and never returns credentials. Upstream failures return the standard API error envelope with a sanitized message.

## Telegram Bot API

`TELEGRAM_PROVIDER=mock` preserves the existing deterministic sender. `TELEGRAM_PROVIDER=bot_api` selects an official HTTPS Bot API provider configured by `TELEGRAM_BOT_TOKEN`, `TELEGRAM_WEBHOOK_SECRET`, and `TELEGRAM_WEBHOOK_BASE_URL`.

The provider implements `getMe`, `sendMessage`, and `setWebhook`. It uses strict timeouts and sanitized errors. Tokens are used only in outbound API URLs and are never logged or included in responses.

`POST /api/v1/telegram/webhook/<connection_id>/` accepts Telegram updates only when the `X-Telegram-Bot-Api-Secret-Token` header matches the configured webhook secret. Updates are idempotently persisted by Telegram update ID. Authorized group and private text messages are mapped to the existing `simulate_incoming_message` workflow, preserving trigger matching, approval, and consent requirements. Unsupported updates return success without creating workflow records so Telegram does not retry them indefinitely.

Workspace owners and admins receive endpoints to test the bot identity and register the webhook. Bot credentials remain global environment-managed platform secrets; connection records contain metadata only.

## Superadmin API

All superadmin endpoints require authenticated Django `is_staff` or `is_superuser` users. They expose read-oriented operational data:

- platform counts for users, active workspaces, opportunities, consent grants, leads, and active Telegram connections;
- searchable workspace rows with owner, member count, lead count, plan, and active state;
- searchable user rows with memberships, staff state, and last login;
- AI and Telegram configuration status with secret-presence booleans, never secret values;
- recent AI request failures, Telegram connection errors, and audit events.

Mutating platform data remains in Django admin for this increment. The React console links directly to relevant Django admin sections.

## Configuration

`.env.example` documents every supported mode without real values. New variables are:

```env
AI_PROVIDER=mock
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash

VERTEX_PROJECT_ID=
VERTEX_LOCATION=us-central1
VERTEX_MODEL=gemini-2.5-flash
GOOGLE_APPLICATION_CREDENTIALS=

TELEGRAM_PROVIDER=mock
TELEGRAM_BOT_TOKEN=
TELEGRAM_WEBHOOK_SECRET=
TELEGRAM_WEBHOOK_BASE_URL=http://localhost:8000
```

Docker Compose passes the `.env` file to backend, worker, and beat. Production can remain in mock mode until the operator adds secrets and switches provider names.

## Error Handling And Security

- Configuration errors identify missing variable names without values.
- External provider exceptions are wrapped in application-specific errors with sanitized messages.
- API keys, bot tokens, webhook secrets, passwords, and credential paths are never returned by APIs or emitted by application logs.
- Superadmin and integration test endpoints enforce role checks in the backend, independent of frontend routing.
- Telegram webhook requests use constant-time secret comparison and idempotent update storage.
- Existing consent checks remain mandatory before product information or lead conversion.

## Testing And Verification

Backend tests cover provider selection, missing configuration, Gemini structured normalization, sanitized failures, owner/admin connection testing, forbidden roles, Telegram provider selection, token-safe errors, webhook secret validation, idempotency, and inbound workflow creation. External SDK and HTTP calls are replaced with injected fake clients at the provider boundary.

Frontend tests cover public routing, authenticated superadmin guards, staff navigation, and critical landing interactions. Production verification includes backend tests, frontend tests, TypeScript build, Django system checks, Docker Compose config validation, browser screenshots at desktop and mobile widths, and deployed health/login/public-page smoke tests.

## Deployment

The existing VPS deployment remains Docker Compose based. Code deploys with mock providers when secrets are absent. After the operator adds `GEMINI_API_KEY` and `TELEGRAM_BOT_TOKEN`, they switch provider names and restart backend, worker, and beat. The deployment documentation includes connection-test and webhook-registration commands. Domain and TLS remain environment/infrastructure concerns because no domain has been supplied.

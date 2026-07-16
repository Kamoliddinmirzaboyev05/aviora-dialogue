# Landing App and Superadmin Design

## Context

Ethical Dialogue AI currently has one Vite React frontend in `frontend/` for the authenticated workspace dashboard. The root route redirects to `/signin`. The backend already exposes staff-only superadmin APIs under `/api/v1/superadmin/`, covering platform overview metrics, workspace rows, user rows, integration status, and recent operational events.

The landing page must be a separate project from the admin panel. The selected architecture is a monorepo with two independent frontend apps:

- `frontend/` remains the authenticated admin/workspace dashboard.
- `landing/` becomes a separate public marketing website with its own package, source tree, build, and test commands.

## Goals

- Add a staff-only superadmin interface inside the existing admin panel.
- Create a separate public landing app in `landing/`.
- Keep landing and admin builds independent so they can be deployed separately.
- Reuse existing backend superadmin API behavior instead of adding new backend endpoints.
- Preserve the current workspace dashboard flows.

## Non-Goals

- Do not combine landing routes into `frontend/`.
- Do not move admin authentication into the landing app.
- Do not expose superadmin data to non-staff users.
- Do not add new backend superadmin capabilities beyond the existing read-only API surface.
- Do not commit local `.env` files.

## Architecture

### Admin Frontend

`frontend/` remains the existing Vite React app. It will gain a new route:

- `/app/superadmin`

The route renders inside `DashboardLayout`, because superadmin is an authenticated operational surface. The sidebar shows a Superadmin item only when the signed-in user has platform staff privileges.

The auth context will expose staff identity flags returned by `/api/v1/auth/me/`:

- `is_staff`
- `is_superuser`

Staff access in the frontend is a UX guard only. The backend remains the source of truth and continues returning `403` for non-staff users.

### Landing App

`landing/` is a separate Vite React app with its own:

- `package.json`
- `index.html`
- `src/`
- Tailwind or CSS setup
- test and build scripts

The landing app does not depend on admin auth state. It links users to the admin sign-in route through a configurable URL, defaulting to the local admin path during development.

The existing `ethical-dialogue-hero.png` asset can be copied into `landing/src/assets/` so the landing app owns the assets it builds with.

## Superadmin Page

The page will be designed as a dense operational dashboard, not a marketing page. It should fit the existing dashboard style: restrained colors, compact cards, clear tables, and predictable controls.

Sections:

- Platform metrics: users, active workspaces, opportunities, consent grants, leads, active Telegram connections.
- Integration status: AI provider/model and credential presence; Telegram provider and required configuration presence.
- Workspaces table: name, business name, industry, owner, members, leads, plan, active state, with search.
- Users table: email, full name, memberships, staff/superuser flags, last login, with search.
- Recent events: AI failures, Telegram connection errors, and audit events.

Data loading:

- Use React Query per API resource.
- Keep tables independently searchable so one slow query does not block the whole page.
- Display loading, empty, and error states for each section.

## Landing Page

The landing app is a public product website for Ethical Dialogue AI. The first screen should communicate the product immediately and include a clear path to sign in.

Sections:

- Hero: brand/product name, concise value proposition, primary sign-in CTA, secondary product workflow CTA.
- Product workflow: Telegram conversations analyzed, consent requested, approved responses, qualified leads.
- Trust and ethics: consent-first messaging, auditability, human approval, privacy-minded integrations.
- Operator value: dashboard, approvals, lead conversion, analytics.
- Final CTA: sign in or request/demo-oriented copy, depending on deployment needs.

Visual direction:

- Use a real bitmap hero asset, starting with `ethical-dialogue-hero.png`.
- Avoid making the landing app look like the admin dashboard.
- Keep the palette professional and varied, without relying on a single hue family.
- Ensure text and buttons fit cleanly on mobile and desktop.

## API Contracts

Existing backend endpoints:

- `GET /api/v1/superadmin/overview/`
- `GET /api/v1/superadmin/workspaces/?search=<query>`
- `GET /api/v1/superadmin/users/?search=<query>`
- `GET /api/v1/superadmin/integrations/`
- `GET /api/v1/superadmin/events/`

The frontend will add typed API helpers for these responses. Pagination can initially show the first page returned by the API.

## Security

- Superadmin navigation is hidden from non-staff users.
- Direct navigation to `/app/superadmin` must show an access-denied state or redirect for non-staff users.
- Backend `IsPlatformStaff` permissions remain authoritative.
- Integration status must show only booleans and provider/model names, never secret values.
- `.env` files remain ignored and are not copied into the landing app.

## Testing

Admin frontend:

- Staff users see the Superadmin nav item.
- Non-staff users do not see the Superadmin nav item.
- Superadmin page renders overview, integrations, workspace/user rows, and recent events from mocked API responses.
- Non-staff access renders an access-denied state.

Landing app:

- Landing page renders the product name, primary CTA, and major sections.
- Build succeeds independently from the admin frontend.

Verification commands:

- `cd frontend && npm test`
- `cd frontend && npm run build`
- `cd landing && npm test`
- `cd landing && npm run build`

## Rollout

1. Add the admin superadmin route, API types, API helpers, and tests in `frontend/`.
2. Add the separate `landing/` app with tests and build config.
3. Update root documentation with separate commands for admin and landing development.
4. Verify both apps independently.


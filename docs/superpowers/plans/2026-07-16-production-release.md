# Production Release Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Document, verify, deploy, and smoke-test the completed production-readiness increment without adding real secrets to source control.

**Architecture:** Environment templates describe selectable provider modes, Docker Compose injects the operator-owned `.env`, and deployment defaults safely to mock providers until secrets are added. Verification covers backend, frontend, configuration, visual rendering, and deployed routes.

**Tech Stack:** Docker Compose, Nginx, Django, Vite, pytest, Vitest, browser automation, SSH.

## Global Constraints

- Real API keys and bot tokens are never committed.
- Production remains available in mock mode when integration secrets are absent.
- Deployment must not overwrite the server's existing `.env`.
- Public landing, sign-in, customer dashboard, superadmin authorization, health, and integration error behavior are smoke-tested.

---

### Task 1: Environment And Documentation

**Files:**
- Modify: `.env.example`
- Modify: `README.md`
- Modify: `docs/AI_PIPELINE.md`
- Modify: `docs/TELEGRAM_SETUP.md`
- Modify: `docs/API.md`
- Modify: `docs/DEPLOYMENT.md`
- Modify: `docs/SECURITY.md`
- Modify: `docs/IMPLEMENTATION_STATUS.md`
- Modify: `docker-compose.yml`
- Modify: `docker-compose.prod.yml`

**Interfaces:**
- Consumes: completed AI, Telegram, landing, and superadmin features.
- Produces: exact configuration, connection-test, webhook-registration, restart, and verification instructions.

- [ ] **Step 1: Validate Compose before changing documentation**

Run: `docker compose config && docker compose -f docker-compose.prod.yml config`

Expected: both commands exit 0.

- [ ] **Step 2: Document provider modes and safe secret setup**

```env
AI_PROVIDER=gemini
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash
TELEGRAM_PROVIDER=bot_api
TELEGRAM_BOT_TOKEN=
TELEGRAM_WEBHOOK_SECRET=
TELEGRAM_WEBHOOK_BASE_URL=https://example.com
```

Include commands that restart backend, worker, and beat after operator edits and authenticated API examples that test AI and Telegram connections without echoing secret values.

- [ ] **Step 3: Validate docs and Compose, then commit**

Run: `rg -n "GEMINI_API_KEY|TELEGRAM_BOT_TOKEN|AI_PROVIDER|TELEGRAM_PROVIDER" .env.example README.md docs && docker compose config && docker compose -f docker-compose.prod.yml config`

Expected: variables and mode instructions are present; Compose commands exit 0.

```bash
git add .env.example README.md docs docker-compose.yml docker-compose.prod.yml
git commit -m "docs: add production integration setup"
```

### Task 2: Full Verification And Visual QA

**Files:**
- Modify only files required by failures found during verification.

**Interfaces:**
- Consumes: full completed codebase.
- Produces: fresh passing evidence and responsive screenshots.

- [ ] **Step 1: Run backend checks and tests**

Run: `cd backend && python manage.py check && pytest -q`

Expected: Django reports no issues and pytest reports zero failures.

- [ ] **Step 2: Run frontend tests and build**

Run: `cd frontend && npm test && npm run build`

Expected: Vitest reports zero failures and Vite exits 0.

- [ ] **Step 3: Run configuration checks**

Run: `docker compose config && docker compose -f docker-compose.prod.yml config && git diff --check`

Expected: every command exits 0.

- [ ] **Step 4: Run browser QA at desktop and mobile sizes**

Open `/`, `/signin`, `/app`, and `/superadmin` at 1440x900 and 390x844. Verify the hero asset renders, text does not overlap, navigation remains usable, reduced-motion styling exists, authenticated customer routes work, and non-staff users cannot display superadmin data.

- [ ] **Step 5: Fix failures test-first and commit**

For each behavior failure, add or adjust the smallest reproducing test, confirm it fails, implement the fix, and rerun the focused and full commands.

```bash
git add -A
git commit -m "fix: address production verification findings"
```

### Task 3: VPS Deployment And Smoke Test

**Files:**
- Modify: `infrastructure/scripts/deploy_vps.sh` only if deployment reveals an in-scope defect.

**Interfaces:**
- Consumes: verified repository and existing VPS `.env`.
- Produces: running deployment with mock providers until the operator supplies secrets.

- [ ] **Step 1: Confirm the worktree is clean and capture the release commit**

Run: `git status --short && git rev-parse --short HEAD`

Expected: no status output and one short commit hash.

- [ ] **Step 2: Sync and rebuild without overwriting `.env`**

Run: `infrastructure/scripts/deploy_vps.sh root@13.140.176.98`

Expected: image builds succeed, containers start, and migrations finish.

- [ ] **Step 3: Run deployed smoke tests**

Run from the VPS or a trusted client:

```bash
curl -fsS http://13.140.176.98:8080/health/
curl -fsSI http://13.140.176.98:8080/
curl -fsSI http://13.140.176.98:8080/signin
```

Expected: health JSON contains `{"status":"ok"}` and public pages return HTTP 200.

- [ ] **Step 4: Verify provider startup behavior without exposing secrets**

Keep the deployed server in `AI_PROVIDER=mock` and `TELEGRAM_PROVIDER=mock` until the operator adds credentials. Confirm the authenticated mock AI connection endpoint returns `connected`; do not print or inspect key values.

- [ ] **Step 5: Record final release status**

Run: `git status --short`

Expected: clean worktree. Report the public URL, configured modes, test totals, known external-secret dependency, and release commit.


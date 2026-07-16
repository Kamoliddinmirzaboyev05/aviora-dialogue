# Separate Superadmin App Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move superadmin out of `frontend/` into a separate Uzbek-language `superadmin/` app.

**Architecture:** `frontend/` becomes workspace-only. `superadmin/` becomes its own Vite React app with scoped token storage, staff auth guard, Uzbek sign-in and platform dashboard screens, and existing backend API integration.

**Tech Stack:** React 19, React Router 7, React Query 5, Vite 7, TypeScript 5.8, Vitest 3, Testing Library, Tailwind CSS, lucide-react.

## Global Constraints

- `superadmin/` must be a separate frontend project.
- `frontend/` must no longer include `/app/superadmin`.
- All visible superadmin app text must be Uzbek.
- Do not add backend endpoints.
- Do not commit `.env` files.
- Backend staff permissions remain authoritative.
- Default ports: `frontend` 5173, `landing` 5174, `superadmin` 5175.

---

### Task 1: Remove Superadmin From Workspace Frontend

**Files:**
- Modify: `frontend/src/app/router.tsx`
- Modify: `frontend/src/layouts/DashboardLayout.tsx`
- Modify: `frontend/src/layouts/DashboardLayout.test.tsx`
- Delete: `frontend/src/pages/SuperadminPage.tsx`
- Delete: `frontend/src/pages/SuperadminPage.test.tsx`
- Modify: `frontend/src/services/api.ts`
- Modify: `frontend/src/types/api.ts`
- Modify: `frontend/src/features/auth/AuthProvider.tsx`

**Interfaces:**
- Produces: Workspace frontend without any superadmin route, nav item, page, API helpers, or tests.

- [ ] Write/adjust failing frontend test proving `Superadmin` nav is absent.
- [ ] Run `cd frontend && npm test -- src/layouts/DashboardLayout.test.tsx` and confirm failure before code removal.
- [ ] Remove route, nav item, page files, and unused superadmin API/types/auth flag.
- [ ] Run `cd frontend && npm test` and `cd frontend && npm run build`.
- [ ] Commit with `chore: remove superadmin from workspace frontend`.

### Task 2: Create Standalone Superadmin App

**Files:**
- Create: `superadmin/package.json`
- Create: `superadmin/index.html`
- Create: `superadmin/vite.config.ts`
- Create: `superadmin/tsconfig.json`
- Create: `superadmin/postcss.config.js`
- Create: `superadmin/tailwind.config.js`
- Create: `superadmin/src/main.tsx`
- Create: `superadmin/src/App.tsx`
- Create: `superadmin/src/App.test.tsx`
- Create: `superadmin/src/styles.css`
- Create: `superadmin/src/test/setup.ts`
- Create: `superadmin/src/services/api.ts`
- Create: `superadmin/src/types/api.ts`

**Interfaces:**
- Produces: `superadmin/` app with `/signin` and `/app`, scoped token storage, staff guard, Uzbek UI, and platform dashboard.

- [ ] Create app scaffolding and a failing test for Uzbek sign-in, staff dashboard, and non-staff access denied.
- [ ] Run `cd superadmin && npm install && npm test` and confirm RED.
- [ ] Implement API client, auth flow, Uzbek UI, and dashboard.
- [ ] Run `cd superadmin && npm test` and `cd superadmin && npm run build`.
- [ ] Commit with `feat: add standalone Uzbek superadmin app`.

### Task 3: Documentation and Verification

**Files:**
- Modify: `README.md`

**Interfaces:**
- Produces: README documenting all three frontend apps.

- [ ] Update README for `landing/`, `frontend/`, and `superadmin/`.
- [ ] Run `cd frontend && npm test && npm run build`.
- [ ] Run `cd landing && npm install && npm test && npm run build`.
- [ ] Run `cd superadmin && npm test && npm run build`.
- [ ] Commit with `docs: document standalone superadmin app`.


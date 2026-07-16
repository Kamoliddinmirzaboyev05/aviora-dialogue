# Product Surfaces Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a polished public landing page and a secure custom superadmin console without disrupting the customer dashboard.

**Architecture:** React Router separates public, customer, and staff-only surfaces. Django exposes read-oriented staff APIs and retains Django admin for low-level mutations. Landing motion is CSS and IntersectionObserver based with reduced-motion support.

**Tech Stack:** React 19, TypeScript, Vite, React Router, TanStack Query, Lucide, Tailwind/CSS, Django REST Framework, pytest, Vitest.

## Global Constraints

- `/` is public, `/app/*` requires a workspace session, and `/superadmin/*` requires backend-verified staff status.
- The landing hero names Ethical Dialogue AI and uses a bitmap product visual.
- UI motion must respect `prefers-reduced-motion`.
- Superadmin APIs never expose secret values.
- Compact operational UI uses cards only for repeated metrics or records and avoids nested cards.

---

### Task 1: Staff Identity And Superadmin API

**Files:**
- Create: `backend/apps/superadmin/__init__.py`
- Create: `backend/apps/superadmin/apps.py`
- Create: `backend/apps/superadmin/permissions.py`
- Create: `backend/apps/superadmin/views.py`
- Create: `backend/apps/superadmin/urls.py`
- Modify: `backend/config/settings.py`
- Modify: `backend/config/urls.py`
- Modify: `backend/apps/accounts/views.py`
- Test: `backend/tests/test_superadmin_api.py`

**Interfaces:**
- Consumes: user, workspace, opportunity, consent, lead, Telegram, AI log, audit, and billing models.
- Produces: staff flag in `/auth/me/`; overview, workspaces, users, integrations, and events endpoints under `/api/v1/superadmin/`.

- [ ] **Step 1: Write forbidden and staff-success tests**

```python
def test_regular_user_cannot_access_superadmin(user_client):
    assert user_client.get("/api/v1/superadmin/overview/").status_code == 403

def test_staff_user_sees_platform_overview(staff_client):
    response = staff_client.get("/api/v1/superadmin/overview/")
    assert response.status_code == 200
    assert set(response.data) >= {"users", "active_workspaces", "opportunities", "consent_grants", "leads", "telegram_connections"}

def test_integrations_return_presence_not_secrets(staff_client, settings):
    settings.GEMINI_API_KEY = "never-return-me"
    response = staff_client.get("/api/v1/superadmin/integrations/")
    assert response.data["ai"]["credential_configured"] is True
    assert "never-return-me" not in str(response.data)
```

- [ ] **Step 2: Run tests and verify RED**

Run: `cd backend && pytest tests/test_superadmin_api.py -q`

Expected: 404 because the superadmin API is not registered.

- [ ] **Step 3: Add staff status to identity response**

```python
"user": {
    "id": str(request.user.id),
    "email": request.user.email,
    "full_name": request.user.full_name,
    "is_staff": request.user.is_staff,
    "is_superuser": request.user.is_superuser,
}
```

- [ ] **Step 4: Implement staff permission and read APIs**

```python
class IsPlatformStaff(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser))
```

Use ORM annotations for searchable workspace and user lists and return explicit secret-presence booleans from the integration endpoint.

- [ ] **Step 5: Run tests and commit**

Run: `cd backend && pytest tests/test_superadmin_api.py tests/test_auth_workspace.py -q`

Expected: all tests pass.

```bash
git add backend/apps/superadmin backend/apps/accounts/views.py backend/config backend/tests/test_superadmin_api.py
git commit -m "feat: add staff-only superadmin API"
```

### Task 2: Public Landing Page

**Files:**
- Create: `frontend/src/pages/LandingPage.tsx`
- Create: `frontend/src/components/landing/Reveal.tsx`
- Create: `frontend/src/components/landing/WorkflowVisual.tsx`
- Create: `frontend/src/assets/ethical-dialogue-hero.webp`
- Modify: `frontend/src/app/router.tsx`
- Modify: `frontend/src/styles.css`
- Test: `frontend/src/pages/LandingPage.test.tsx`

**Interfaces:**
- Consumes: generated hero bitmap asset, React Router links.
- Produces: public `/` page with mobile navigation, workflow, capability, trust, preview, and CTA sections.

- [ ] **Step 1: Write the route and core-content test**

```tsx
it("renders the public product offer and sign-in action", () => {
  render(<MemoryRouter><LandingPage /></MemoryRouter>);
  expect(screen.getByRole("heading", { name: "Ethical Dialogue AI" })).toBeInTheDocument();
  expect(screen.getByRole("link", { name: /sign in/i })).toHaveAttribute("href", "/signin");
  expect(screen.getByText(/permission before promotion/i)).toBeInTheDocument();
});
```

- [ ] **Step 2: Run the test and verify RED**

Run: `cd frontend && npm test -- LandingPage.test.tsx`

Expected: import failure because `LandingPage` does not exist.

- [ ] **Step 3: Generate and add the hero bitmap**

Create a wide editorial product visual showing a Telegram conversation entering an AI relevance classifier, an explicit permission checkpoint, and a qualified lead result. Use crisp readable interface shapes, a light foundation, teal/coral/lime accents, no logos from third parties, and no embedded small text.

- [ ] **Step 4: Implement the semantic responsive landing page**

```tsx
export function LandingPage() {
  return <div className="landing-shell">
    <header className="landing-nav">...</header>
    <main>
      <section className="landing-hero" aria-labelledby="landing-title">...</section>
      <section id="workflow">...</section>
      <section id="capabilities">...</section>
      <section id="trust">...</section>
      <section id="product-preview">...</section>
      <section id="get-started">...</section>
    </main>
    <footer>...</footer>
  </div>;
}
```

- [ ] **Step 5: Add motion with reduced-motion fallback**

```css
@media (prefers-reduced-motion: reduce) {
  .reveal, .workflow-pulse, .hero-media img { animation: none !important; transition: none !important; transform: none !important; }
}
```

- [ ] **Step 6: Run tests, build, and commit**

Run: `cd frontend && npm test -- LandingPage.test.tsx && npm run build`

Expected: test and TypeScript production build pass.

```bash
git add frontend/src/pages/LandingPage.tsx frontend/src/pages/LandingPage.test.tsx frontend/src/components/landing frontend/src/assets frontend/src/app/router.tsx frontend/src/styles.css
git commit -m "feat: add animated public landing page"
```

### Task 3: React Superadmin Console

**Files:**
- Create: `frontend/src/layouts/SuperadminLayout.tsx`
- Create: `frontend/src/pages/superadmin/SuperadminOverviewPage.tsx`
- Create: `frontend/src/pages/superadmin/SuperadminWorkspacesPage.tsx`
- Create: `frontend/src/pages/superadmin/SuperadminUsersPage.tsx`
- Create: `frontend/src/pages/superadmin/SuperadminIntegrationsPage.tsx`
- Create: `frontend/src/pages/superadmin/SuperadminEventsPage.tsx`
- Modify: `frontend/src/app/router.tsx`
- Modify: `frontend/src/features/auth/AuthProvider.tsx`
- Modify: `frontend/src/services/api.ts`
- Modify: `frontend/src/types/api.ts`
- Modify: `frontend/src/styles.css`
- Test: `frontend/src/pages/superadmin/SuperadminOverviewPage.test.tsx`

**Interfaces:**
- Consumes: staff identity and `/superadmin/*` API responses.
- Produces: frontend staff guard, overview metrics, searchable tables, health states, event list, Django admin links.

- [ ] **Step 1: Write staff guard and overview tests**

```tsx
it("redirects a non-staff user away from superadmin", () => {
  renderSuperadmin({ is_staff: false });
  expect(mockNavigate).toHaveBeenCalledWith("/app", { replace: true });
});

it("shows platform metrics for staff", async () => {
  renderSuperadmin({ is_staff: true });
  expect(await screen.findByText("Platform overview")).toBeInTheDocument();
  expect(screen.getByText("Active workspaces")).toBeInTheDocument();
});
```

- [ ] **Step 2: Run tests and verify RED**

Run: `cd frontend && npm test -- SuperadminOverviewPage.test.tsx`

Expected: imports fail because the superadmin components do not exist.

- [ ] **Step 3: Extend identity types and API client**

```ts
export type PlatformUser = { id: string; email: string; full_name: string; is_staff: boolean; is_superuser: boolean };
superadminOverview: () => request<SuperadminOverview>("/superadmin/overview/"),
```

- [ ] **Step 4: Implement the guarded layout and compact pages**

```tsx
if (!auth.me?.user.is_staff && !auth.me?.user.is_superuser) return <Navigate to="/app" replace />;
```

Use Lucide icons, compact 8px-or-less radii, stable table columns, status badges, empty states, loading states, and actionable links to `/admin/`.

- [ ] **Step 5: Run tests, build, and commit**

Run: `cd frontend && npm test -- SuperadminOverviewPage.test.tsx && npm run build`

Expected: tests and production build pass.

```bash
git add frontend/src/layouts/SuperadminLayout.tsx frontend/src/pages/superadmin frontend/src/app/router.tsx frontend/src/features/auth/AuthProvider.tsx frontend/src/services/api.ts frontend/src/types/api.ts frontend/src/styles.css
git commit -m "feat: add custom superadmin console"
```

### Task 4: Operational Django Admin

**Files:**
- Create: `backend/apps/workspaces/admin.py`
- Create: `backend/apps/products/admin.py`
- Create: `backend/apps/triggers/admin.py`
- Create: `backend/apps/telegram_integration/admin.py`
- Create: `backend/apps/opportunities/admin.py`
- Create: `backend/apps/conversations/admin.py`
- Create: `backend/apps/consent/admin.py`
- Create: `backend/apps/leads/admin.py`
- Create: `backend/apps/ai_engine/admin.py`
- Create: `backend/apps/audit_logs/admin.py`
- Modify: `backend/config/settings.py`
- Test: `backend/tests/test_django_admin.py`

**Interfaces:**
- Consumes: all operational domain models.
- Produces: searchable, filterable, safe Django admin registrations and branded admin headings.

- [ ] **Step 1: Write admin registration and access tests**

```python
def test_superuser_can_open_registered_domain_admin(superuser_client):
    assert superuser_client.get("/admin/workspaces/workspace/").status_code == 200
    assert superuser_client.get("/admin/leads/lead/").status_code == 200

def test_non_staff_cannot_open_django_admin(user_client):
    assert user_client.get("/admin/").status_code == 302
```

- [ ] **Step 2: Run tests and verify RED**

Run: `cd backend && pytest tests/test_django_admin.py -q`

Expected: domain changelist routes return 404 because models are not registered.

- [ ] **Step 3: Register models with operational columns and readonly audit fields**

```python
@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ("name", "business_name", "industry", "is_active", "created_at")
    list_filter = ("is_active", "industry")
    search_fields = ("name", "business_name", "slug")
    readonly_fields = ("id", "created_at", "updated_at")
```

- [ ] **Step 4: Set admin brand labels, run tests, and commit**

```python
admin.site.site_header = "Ethical Dialogue AI Operations"
admin.site.site_title = "Ethical Dialogue AI Admin"
admin.site.index_title = "Platform operations"
```

Run: `cd backend && pytest tests/test_django_admin.py -q`

Expected: all admin tests pass.

```bash
git add backend/apps/*/admin.py backend/config/settings.py backend/tests/test_django_admin.py
git commit -m "feat: configure operational Django admin"
```


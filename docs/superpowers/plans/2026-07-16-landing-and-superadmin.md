# Landing App and Superadmin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a staff-only superadmin surface inside the existing admin frontend and add a separate public `landing/` Vite React app.

**Architecture:** Keep `frontend/` as the authenticated admin/workspace dashboard and add `/app/superadmin` there. Add `landing/` as an independent Vite React app with its own package, source tree, tests, and build. Reuse the existing backend superadmin APIs without adding new backend endpoints.

**Tech Stack:** React 19, React Router 7, React Query 5, Vite 7, TypeScript 5.8, Vitest 3, Testing Library, Tailwind CSS, lucide-react.

## Global Constraints

- `frontend/` remains the authenticated admin/workspace dashboard.
- `landing/` is a separate public marketing website with its own package, source tree, build, and test commands.
- Do not combine landing routes into `frontend/`.
- Do not move admin authentication into the landing app.
- Do not expose superadmin data to non-staff users.
- Do not add new backend superadmin capabilities beyond the existing read-only API surface.
- Do not commit local `.env` files.
- Backend `IsPlatformStaff` permissions remain authoritative.
- Integration status must show only booleans and provider/model names, never secret values.

---

## File Structure

- Modify `frontend/vite.config.ts`: add Vitest `jsdom` configuration for component tests.
- Create `frontend/src/test/setup.ts`: register Testing Library matchers.
- Modify `frontend/src/types/api.ts`: add staff flags to `MeResponse` and add superadmin response types.
- Modify `frontend/src/services/api.ts`: add typed superadmin API helpers.
- Modify `frontend/src/features/auth/AuthProvider.tsx`: expose `isPlatformStaff`.
- Create `frontend/src/layouts/DashboardLayout.test.tsx`: test staff-only navigation.
- Modify `frontend/src/layouts/DashboardLayout.tsx`: add staff-only Superadmin nav item.
- Create `frontend/src/pages/SuperadminPage.tsx`: render the operational dashboard.
- Create `frontend/src/pages/SuperadminPage.test.tsx`: test staff guard and rendered data.
- Modify `frontend/src/app/router.tsx`: add `/app/superadmin`.
- Create `landing/package.json`: independent landing app scripts and dependencies.
- Create `landing/index.html`: landing app HTML entry.
- Create `landing/vite.config.ts`: Vite and Vitest config for landing.
- Create `landing/tsconfig.json`: TypeScript config.
- Create `landing/postcss.config.js`: PostCSS config.
- Create `landing/tailwind.config.js`: Tailwind config.
- Create `landing/src/main.tsx`: React entrypoint.
- Create `landing/src/App.tsx`: landing page UI.
- Create `landing/src/App.test.tsx`: landing render test.
- Create `landing/src/styles.css`: landing styles.
- Copy `frontend/src/assets/ethical-dialogue-hero.png` to `landing/src/assets/ethical-dialogue-hero.png`.
- Modify `README.md`: document separate admin and landing commands.

---

### Task 1: Staff Identity, API Helpers, and Superadmin Navigation

**Files:**
- Modify: `frontend/vite.config.ts`
- Create: `frontend/src/test/setup.ts`
- Modify: `frontend/src/types/api.ts`
- Modify: `frontend/src/services/api.ts`
- Modify: `frontend/src/features/auth/AuthProvider.tsx`
- Modify: `frontend/src/layouts/DashboardLayout.tsx`
- Create: `frontend/src/layouts/DashboardLayout.test.tsx`

**Interfaces:**
- Consumes: Existing `/api/v1/auth/me/` response, existing auth context, existing dashboard layout.
- Produces:
  - `MeResponse["user"].is_staff: boolean`
  - `MeResponse["user"].is_superuser: boolean`
  - `useAuth().isPlatformStaff: boolean`
  - `api.superadminOverview(): Promise<SuperadminOverview>`
  - `api.superadminWorkspaces(search?: string): Promise<Paginated<SuperadminWorkspace>>`
  - `api.superadminUsers(search?: string): Promise<Paginated<SuperadminUser>>`
  - `api.superadminIntegrations(): Promise<SuperadminIntegrations>`
  - `api.superadminEvents(): Promise<Paginated<SuperadminEvent>>`

- [ ] **Step 1: Write the failing navigation test**

Create `frontend/src/layouts/DashboardLayout.test.tsx`:

```tsx
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, test, vi } from "vitest";

import { DashboardLayout } from "./DashboardLayout";
import { AuthProvider } from "../features/auth/AuthProvider";
import { tokenStore } from "../services/api";

vi.mock("../services/api", async () => {
  const actual = await vi.importActual<typeof import("../services/api")>("../services/api");
  return {
    ...actual,
    tokenStore: {
      access: "test-token",
      set: vi.fn(),
      clear: vi.fn()
    },
    api: {
      ...actual.api,
      me: vi.fn()
    }
  };
});

const { api } = await import("../services/api");

beforeEach(() => {
  vi.clearAllMocks();
});

function renderLayout(isStaff: boolean) {
  vi.mocked(api.me).mockResolvedValue({
    user: {
      id: "user-1",
      email: isStaff ? "staff@example.com" : "owner@example.com",
      full_name: isStaff ? "Staff User" : "Owner User",
      is_staff: isStaff,
      is_superuser: false
    },
    memberships: [
      {
        id: "membership-1",
        role: "owner",
        workspace: {
          id: "workspace-1",
          name: "Demo Workspace",
          slug: "demo",
          business_name: "Demo Business"
        }
      }
    ]
  });

  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } }
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <MemoryRouter initialEntries={["/app"]}>
          <Routes>
            <Route path="/app" element={<DashboardLayout />}>
              <Route index element={<div>Dashboard home</div>} />
            </Route>
          </Routes>
        </MemoryRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}

describe("DashboardLayout", () => {
  test("shows the Superadmin nav item to staff users", async () => {
    renderLayout(true);

    expect(await screen.findByRole("link", { name: /superadmin/i })).toHaveAttribute(
      "href",
      "/app/superadmin"
    );
  });

  test("hides the Superadmin nav item from non-staff users", async () => {
    renderLayout(false);

    expect(await screen.findByText("Dashboard home")).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: /superadmin/i })).not.toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run the navigation test to verify it fails**

Run:

```bash
cd frontend && npm test -- src/layouts/DashboardLayout.test.tsx
```

Expected: FAIL because Vitest is not configured for `jsdom`, `toBeInTheDocument` setup is missing, or `Superadmin` navigation is not implemented.

- [ ] **Step 3: Add Vitest setup**

Replace `frontend/vite.config.ts` with:

```ts
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  server: {
    host: "0.0.0.0",
    port: 5173
  },
  test: {
    environment: "jsdom",
    setupFiles: "./src/test/setup.ts",
    globals: false
  }
});
```

Create `frontend/src/test/setup.ts`:

```ts
import "@testing-library/jest-dom/vitest";
```

- [ ] **Step 4: Add API types**

Update `frontend/src/types/api.ts` so the `MeResponse` user includes staff flags:

```ts
export type MeResponse = {
  user: {
    id: string;
    email: string;
    full_name: string;
    is_staff: boolean;
    is_superuser: boolean;
  };
  memberships: Array<{ id: string; role: string; workspace: Workspace }>;
};
```

Append these types to `frontend/src/types/api.ts`:

```ts
export type SuperadminOverview = {
  users: number;
  active_workspaces: number;
  opportunities: number;
  consent_grants: number;
  leads: number;
  telegram_connections: number;
};

export type SuperadminWorkspace = {
  id: string;
  name: string;
  business_name: string;
  industry: string;
  is_active: boolean;
  owner: string | null;
  member_count: number;
  lead_count: number;
  plan: string | null;
};

export type SuperadminUser = {
  id: string;
  email: string;
  full_name: string;
  membership_count: number;
  is_staff: boolean;
  is_superuser: boolean;
  last_login: string | null;
};

export type SuperadminIntegrations = {
  ai: {
    provider: string;
    model: string;
    credential_configured: boolean;
    vertex_project_configured: boolean;
  };
  telegram: {
    provider: string;
    bot_token_configured: boolean;
    webhook_secret_configured: boolean;
    webhook_base_url_configured: boolean;
  };
};

export type SuperadminEvent = {
  id: string;
  source: string;
  workspace: string;
  created_at: string;
  summary: string;
};
```

- [ ] **Step 5: Add API helper methods**

Update the import in `frontend/src/services/api.ts`:

```ts
import type {
  Analytics,
  Conversation,
  Draft,
  Lead,
  MeResponse,
  Opportunity,
  Paginated,
  SuperadminEvent,
  SuperadminIntegrations,
  SuperadminOverview,
  SuperadminUser,
  SuperadminWorkspace,
  Workspace
} from "../types/api";
```

Add this helper near `request`:

```ts
function searchParam(search?: string) {
  const trimmed = search?.trim();
  return trimmed ? `?search=${encodeURIComponent(trimmed)}` : "";
}
```

Add these methods inside the exported `api` object:

```ts
  superadminOverview: () => request<SuperadminOverview>("/superadmin/overview/"),
  superadminWorkspaces: (search?: string) =>
    request<Paginated<SuperadminWorkspace>>(`/superadmin/workspaces/${searchParam(search)}`),
  superadminUsers: (search?: string) =>
    request<Paginated<SuperadminUser>>(`/superadmin/users/${searchParam(search)}`),
  superadminIntegrations: () => request<SuperadminIntegrations>("/superadmin/integrations/"),
  superadminEvents: () => request<Paginated<SuperadminEvent>>("/superadmin/events/"),
```

- [ ] **Step 6: Expose platform staff state**

Update `AuthContextValue` in `frontend/src/features/auth/AuthProvider.tsx`:

```ts
type AuthContextValue = {
  me?: MeResponse;
  workspace?: Workspace;
  isAuthenticated: boolean;
  isLoading: boolean;
  isPlatformStaff: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signOut: () => void;
};
```

Add `isPlatformStaff` in the memoized value:

```ts
      isPlatformStaff: Boolean(meQuery.data?.user.is_staff || meQuery.data?.user.is_superuser),
```

- [ ] **Step 7: Add staff-only Superadmin navigation**

Update the lucide import in `frontend/src/layouts/DashboardLayout.tsx`:

```tsx
import { Activity, Bot, CheckSquare, LineChart, MessageSquare, Package, Radio, Settings, ShieldCheck, Target, Users } from "lucide-react";
```

Inside `DashboardLayout`, after the auth guard, add:

```tsx
  const visibleNav = auth.isPlatformStaff
    ? [...nav, { to: "/app/superadmin", label: "Superadmin", icon: ShieldCheck }]
    : nav;
```

Change the nav rendering loop from `nav.map` to `visibleNav.map`.

- [ ] **Step 8: Run the navigation test to verify it passes**

Run:

```bash
cd frontend && npm test -- src/layouts/DashboardLayout.test.tsx
```

Expected: PASS.

- [ ] **Step 9: Commit Task 1**

```bash
git add frontend/vite.config.ts frontend/src/test/setup.ts frontend/src/types/api.ts frontend/src/services/api.ts frontend/src/features/auth/AuthProvider.tsx frontend/src/layouts/DashboardLayout.tsx frontend/src/layouts/DashboardLayout.test.tsx
git commit -m "feat: add staff-only superadmin navigation"
```

---

### Task 2: Superadmin Page

**Files:**
- Create: `frontend/src/pages/SuperadminPage.tsx`
- Create: `frontend/src/pages/SuperadminPage.test.tsx`
- Modify: `frontend/src/app/router.tsx`

**Interfaces:**
- Consumes:
  - `useAuth().isPlatformStaff: boolean`
  - `api.superadminOverview`
  - `api.superadminWorkspaces`
  - `api.superadminUsers`
  - `api.superadminIntegrations`
  - `api.superadminEvents`
- Produces: `/app/superadmin` route rendering a staff-only dashboard.

- [ ] **Step 1: Write the failing superadmin page test**

Create `frontend/src/pages/SuperadminPage.test.tsx`:

```tsx
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, test, vi } from "vitest";

import { SuperadminPage } from "./SuperadminPage";

vi.mock("../features/auth/AuthProvider", () => ({
  useAuth: vi.fn()
}));

vi.mock("../services/api", async () => {
  const actual = await vi.importActual<typeof import("../services/api")>("../services/api");
  return {
    ...actual,
    api: {
      ...actual.api,
      superadminOverview: vi.fn(),
      superadminWorkspaces: vi.fn(),
      superadminUsers: vi.fn(),
      superadminIntegrations: vi.fn(),
      superadminEvents: vi.fn()
    }
  };
});

const { useAuth } = await import("../features/auth/AuthProvider");
const { api } = await import("../services/api");

beforeEach(() => {
  vi.clearAllMocks();
});

function renderPage(isPlatformStaff = true) {
  vi.mocked(useAuth).mockReturnValue({
    me: undefined,
    workspace: undefined,
    isAuthenticated: true,
    isLoading: false,
    isPlatformStaff,
    signIn: vi.fn(),
    signOut: vi.fn()
  });

  vi.mocked(api.superadminOverview).mockResolvedValue({
    users: 12,
    active_workspaces: 3,
    opportunities: 44,
    consent_grants: 20,
    leads: 15,
    telegram_connections: 2
  });
  vi.mocked(api.superadminIntegrations).mockResolvedValue({
    ai: {
      provider: "mock",
      model: "gemini-2.5-flash",
      credential_configured: true,
      vertex_project_configured: false
    },
    telegram: {
      provider: "mock",
      bot_token_configured: false,
      webhook_secret_configured: true,
      webhook_base_url_configured: true
    }
  });
  vi.mocked(api.superadminWorkspaces).mockResolvedValue({
    count: 1,
    next: null,
    previous: null,
    results: [
      {
        id: "workspace-1",
        name: "Northwind Sales",
        business_name: "Northwind Traders",
        industry: "Retail",
        is_active: true,
        owner: "owner@example.com",
        member_count: 2,
        lead_count: 8,
        plan: "Growth"
      }
    ]
  });
  vi.mocked(api.superadminUsers).mockResolvedValue({
    count: 1,
    next: null,
    previous: null,
    results: [
      {
        id: "user-1",
        email: "owner@example.com",
        full_name: "Workspace Owner",
        membership_count: 1,
        is_staff: false,
        is_superuser: false,
        last_login: null
      }
    ]
  });
  vi.mocked(api.superadminEvents).mockResolvedValue({
    count: 1,
    next: null,
    previous: null,
    results: [
      {
        id: "event-1",
        source: "ai_request_failure",
        workspace: "Northwind Sales",
        created_at: "2026-07-16T10:00:00Z",
        summary: "AI classify_message request failed."
      }
    ]
  });

  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } }
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <SuperadminPage />
    </QueryClientProvider>
  );
}

describe("SuperadminPage", () => {
  test("renders platform metrics and operational rows for staff", async () => {
    renderPage(true);

    expect(await screen.findByText("Platform Operations")).toBeInTheDocument();
    expect(await screen.findByText("Northwind Sales")).toBeInTheDocument();
    expect(await screen.findByText("owner@example.com")).toBeInTheDocument();
    expect(await screen.findByText("AI classify_message request failed.")).toBeInTheDocument();
    expect(screen.getAllByText("mock").length).toBeGreaterThan(0);
  });

  test("renders access denied for non-staff users", () => {
    renderPage(false);

    expect(screen.getByText("Access denied")).toBeInTheDocument();
    expect(api.superadminOverview).not.toHaveBeenCalled();
  });
});
```

- [ ] **Step 2: Run the page test to verify it fails**

Run:

```bash
cd frontend && npm test -- src/pages/SuperadminPage.test.tsx
```

Expected: FAIL because `SuperadminPage` does not exist.

- [ ] **Step 3: Implement the superadmin page**

Create `frontend/src/pages/SuperadminPage.tsx`:

```tsx
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, CheckCircle2, Search, ShieldCheck, XCircle } from "lucide-react";

import { Badge } from "../components/ui/Badge";
import { Card } from "../components/ui/Card";
import { useAuth } from "../features/auth/AuthProvider";
import { api } from "../services/api";

const metricLabels = {
  users: "Users",
  active_workspaces: "Active workspaces",
  opportunities: "Opportunities",
  consent_grants: "Consent grants",
  leads: "Leads",
  telegram_connections: "Telegram connections"
};

function StatusMark({ ok }: { ok: boolean }) {
  return (
    <span className={`inline-flex items-center gap-1 text-sm ${ok ? "text-emerald-700" : "text-red-700"}`}>
      {ok ? <CheckCircle2 size={16} /> : <XCircle size={16} />}
      {ok ? "Configured" : "Missing"}
    </span>
  );
}

function LoadingLine() {
  return <p className="text-sm text-slate-500">Loading</p>;
}

function ErrorLine() {
  return <p className="text-sm text-red-700">Unable to load this section.</p>;
}

export function SuperadminPage() {
  const auth = useAuth();
  const [workspaceSearch, setWorkspaceSearch] = useState("");
  const [userSearch, setUserSearch] = useState("");

  const enabled = auth.isPlatformStaff;
  const overview = useQuery({ queryKey: ["superadmin", "overview"], queryFn: api.superadminOverview, enabled });
  const integrations = useQuery({ queryKey: ["superadmin", "integrations"], queryFn: api.superadminIntegrations, enabled });
  const workspaces = useQuery({
    queryKey: ["superadmin", "workspaces", workspaceSearch],
    queryFn: () => api.superadminWorkspaces(workspaceSearch),
    enabled
  });
  const users = useQuery({
    queryKey: ["superadmin", "users", userSearch],
    queryFn: () => api.superadminUsers(userSearch),
    enabled
  });
  const events = useQuery({ queryKey: ["superadmin", "events"], queryFn: api.superadminEvents, enabled });

  if (!auth.isPlatformStaff) {
    return (
      <Card className="flex items-start gap-3">
        <AlertTriangle className="mt-1 text-amber" size={22} />
        <div>
          <h1 className="text-xl font-semibold">Access denied</h1>
          <p className="mt-1 text-sm text-slate-600">This area is only available to platform staff.</p>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm font-medium text-teal">Superadmin</p>
          <h1 className="text-2xl font-semibold">Platform Operations</h1>
        </div>
        <Badge>Staff only</Badge>
      </div>

      <section className="grid gap-3 md:grid-cols-3 xl:grid-cols-6">
        {overview.isLoading && <LoadingLine />}
        {overview.isError && <ErrorLine />}
        {overview.data &&
          Object.entries(metricLabels).map(([key, label]) => (
            <Card key={key}>
              <p className="text-xs font-medium uppercase text-slate-500">{label}</p>
              <p className="mt-2 text-2xl font-semibold">{overview.data[key as keyof typeof metricLabels]}</p>
            </Card>
          ))}
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <Card>
          <div className="mb-4 flex items-center gap-2">
            <ShieldCheck size={18} className="text-teal" />
            <h2 className="font-semibold">AI integration</h2>
          </div>
          {integrations.isLoading && <LoadingLine />}
          {integrations.isError && <ErrorLine />}
          {integrations.data && (
            <dl className="grid gap-3 text-sm">
              <div className="flex justify-between gap-4"><dt className="text-slate-500">Provider</dt><dd>{integrations.data.ai.provider}</dd></div>
              <div className="flex justify-between gap-4"><dt className="text-slate-500">Model</dt><dd>{integrations.data.ai.model}</dd></div>
              <div className="flex justify-between gap-4"><dt className="text-slate-500">Credential</dt><dd><StatusMark ok={integrations.data.ai.credential_configured} /></dd></div>
              <div className="flex justify-between gap-4"><dt className="text-slate-500">Vertex project</dt><dd><StatusMark ok={integrations.data.ai.vertex_project_configured} /></dd></div>
            </dl>
          )}
        </Card>

        <Card>
          <div className="mb-4 flex items-center gap-2">
            <ShieldCheck size={18} className="text-teal" />
            <h2 className="font-semibold">Telegram integration</h2>
          </div>
          {integrations.isLoading && <LoadingLine />}
          {integrations.isError && <ErrorLine />}
          {integrations.data && (
            <dl className="grid gap-3 text-sm">
              <div className="flex justify-between gap-4"><dt className="text-slate-500">Provider</dt><dd>{integrations.data.telegram.provider}</dd></div>
              <div className="flex justify-between gap-4"><dt className="text-slate-500">Bot token</dt><dd><StatusMark ok={integrations.data.telegram.bot_token_configured} /></dd></div>
              <div className="flex justify-between gap-4"><dt className="text-slate-500">Webhook secret</dt><dd><StatusMark ok={integrations.data.telegram.webhook_secret_configured} /></dd></div>
              <div className="flex justify-between gap-4"><dt className="text-slate-500">Webhook URL</dt><dd><StatusMark ok={integrations.data.telegram.webhook_base_url_configured} /></dd></div>
            </dl>
          )}
        </Card>
      </section>

      <section className="grid gap-4 xl:grid-cols-2">
        <Card>
          <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <h2 className="font-semibold">Workspaces</h2>
            <label className="flex items-center gap-2 rounded-md border border-line px-3 py-2 text-sm">
              <Search size={16} />
              <input className="w-48 bg-transparent outline-none" value={workspaceSearch} onChange={(event) => setWorkspaceSearch(event.target.value)} placeholder="Search workspaces" />
            </label>
          </div>
          {workspaces.isLoading && <LoadingLine />}
          {workspaces.isError && <ErrorLine />}
          {workspaces.data && (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="text-xs uppercase text-slate-500">
                  <tr><th className="py-2">Name</th><th>Owner</th><th>Plan</th><th>Leads</th><th>Status</th></tr>
                </thead>
                <tbody className="divide-y divide-line">
                  {workspaces.data.results.map((workspace) => (
                    <tr key={workspace.id}>
                      <td className="py-3"><p className="font-medium">{workspace.name}</p><p className="text-xs text-slate-500">{workspace.business_name} · {workspace.industry}</p></td>
                      <td>{workspace.owner ?? "No active owner"}</td>
                      <td>{workspace.plan ?? "No plan"}</td>
                      <td>{workspace.lead_count}</td>
                      <td>{workspace.is_active ? "Active" : "Inactive"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>

        <Card>
          <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <h2 className="font-semibold">Users</h2>
            <label className="flex items-center gap-2 rounded-md border border-line px-3 py-2 text-sm">
              <Search size={16} />
              <input className="w-48 bg-transparent outline-none" value={userSearch} onChange={(event) => setUserSearch(event.target.value)} placeholder="Search users" />
            </label>
          </div>
          {users.isLoading && <LoadingLine />}
          {users.isError && <ErrorLine />}
          {users.data && (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="text-xs uppercase text-slate-500">
                  <tr><th className="py-2">Email</th><th>Name</th><th>Memberships</th><th>Role</th></tr>
                </thead>
                <tbody className="divide-y divide-line">
                  {users.data.results.map((user) => (
                    <tr key={user.id}>
                      <td className="py-3">{user.email}</td>
                      <td>{user.full_name || "No name"}</td>
                      <td>{user.membership_count}</td>
                      <td>{user.is_superuser ? "Superuser" : user.is_staff ? "Staff" : "Member"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      </section>

      <Card>
        <h2 className="mb-4 font-semibold">Recent events</h2>
        {events.isLoading && <LoadingLine />}
        {events.isError && <ErrorLine />}
        {events.data && (
          <div className="divide-y divide-line">
            {events.data.results.map((event) => (
              <div key={event.id} className="flex flex-col gap-1 py-3 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="font-medium">{event.summary}</p>
                  <p className="text-sm text-slate-500">{event.workspace} · {event.source}</p>
                </div>
                <time className="text-sm text-slate-500">{new Date(event.created_at).toLocaleString()}</time>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
```

- [ ] **Step 4: Register the route**

Modify `frontend/src/app/router.tsx` imports:

```tsx
import { SuperadminPage } from "../pages/SuperadminPage";
```

Add this child route under `/app`:

```tsx
      { path: "superadmin", element: <SuperadminPage /> }
```

- [ ] **Step 5: Run the page test to verify it passes**

Run:

```bash
cd frontend && npm test -- src/pages/SuperadminPage.test.tsx
```

Expected: PASS.

- [ ] **Step 6: Run the admin frontend test suite**

Run:

```bash
cd frontend && npm test
```

Expected: PASS.

- [ ] **Step 7: Commit Task 2**

```bash
git add frontend/src/pages/SuperadminPage.tsx frontend/src/pages/SuperadminPage.test.tsx frontend/src/app/router.tsx
git commit -m "feat: add superadmin dashboard"
```

---

### Task 3: Separate Landing App

**Files:**
- Create: `landing/package.json`
- Create: `landing/index.html`
- Create: `landing/vite.config.ts`
- Create: `landing/tsconfig.json`
- Create: `landing/postcss.config.js`
- Create: `landing/tailwind.config.js`
- Create: `landing/src/main.tsx`
- Create: `landing/src/App.tsx`
- Create: `landing/src/App.test.tsx`
- Create: `landing/src/styles.css`
- Create: `landing/src/test/setup.ts`
- Create: `landing/src/assets/ethical-dialogue-hero.png`

**Interfaces:**
- Consumes: `frontend/src/assets/ethical-dialogue-hero.png`.
- Produces: independent landing app runnable with `cd landing && npm run dev`, testable with `cd landing && npm test`, buildable with `cd landing && npm run build`.

- [ ] **Step 1: Create landing package and config files**

Create `landing/package.json`:

```json
{
  "name": "ethical-dialogue-ai-landing",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite --host 0.0.0.0 --port 5174",
    "build": "tsc -b && vite build",
    "preview": "vite preview --host 0.0.0.0 --port 4174",
    "test": "vitest run"
  },
  "dependencies": {
    "@vitejs/plugin-react": "^5.0.0",
    "vite": "^7.0.0",
    "typescript": "^5.8.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "lucide-react": "^0.468.0"
  },
  "devDependencies": {
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "vitest": "^3.0.0",
    "@testing-library/react": "^16.0.0",
    "@testing-library/jest-dom": "^6.0.0",
    "jsdom": "^26.0.0",
    "tailwindcss": "^3.4.0",
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0"
  }
}
```

Create `landing/index.html`:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Ethical Dialogue AI</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

Create `landing/vite.config.ts`:

```ts
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    setupFiles: "./src/test/setup.ts",
    globals: false
  }
});
```

Create `landing/tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "useDefineForClassFields": true,
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "allowJs": false,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "module": "ESNext",
    "moduleResolution": "Node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx"
  },
  "include": ["src"]
}
```

Create `landing/postcss.config.js`:

```js
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {}
  }
};
```

Create `landing/tailwind.config.js`:

```js
/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#16211f",
        moss: "#355e4b",
        coral: "#c75f4a",
        gold: "#d69f38",
        cloud: "#f4f7f4",
        line: "#d8dfd8"
      }
    }
  },
  plugins: []
};
```

Create `landing/src/test/setup.ts`:

```ts
import "@testing-library/jest-dom/vitest";
```

Create `landing/src/main.tsx`:

```tsx
import React from "react";
import ReactDOM from "react-dom/client";

import { App } from "./App";
import "./styles.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

- [ ] **Step 2: Copy the hero asset**

Run:

```bash
mkdir -p landing/src/assets
cp frontend/src/assets/ethical-dialogue-hero.png landing/src/assets/ethical-dialogue-hero.png
```

- [ ] **Step 3: Write the failing landing render test**

Create `landing/src/App.test.tsx`:

```tsx
import { render, screen } from "@testing-library/react";
import { describe, expect, test } from "vitest";

import { App } from "./App";

describe("App", () => {
  test("renders the product landing page with primary sections", () => {
    render(<App />);

    expect(screen.getByRole("heading", { name: /Ethical Dialogue AI/i })).toBeInTheDocument();
    expect(screen.getAllByRole("link", { name: /Sign in/i })[0]).toHaveAttribute("href", "/signin");
    expect(screen.getByText(/Consent-first automation/i)).toBeInTheDocument();
    expect(screen.getByText(/Telegram conversations/i)).toBeInTheDocument();
    expect(screen.getByText(/Human approval/i)).toBeInTheDocument();
  });
});
```

- [ ] **Step 4: Run the landing test to verify it fails**

Run:

```bash
cd landing && npm install && npm test
```

Expected: FAIL because `landing/src/App.tsx` and `landing/src/styles.css` do not exist.

- [ ] **Step 5: Implement landing page UI**

Create `landing/src/App.tsx`:

```tsx
import { ArrowRight, CheckCircle2, MessageSquareText, ShieldCheck, Sparkles, UserCheck } from "lucide-react";

import heroImage from "./assets/ethical-dialogue-hero.png";

const adminUrl = import.meta.env.VITE_ADMIN_URL ?? "/signin";

const workflow = [
  { title: "Telegram conversations", text: "Monitor product questions and buyer intent without turning private chats into a black box.", icon: MessageSquareText },
  { title: "Consent requested", text: "Ask permission before product recommendations move into a more guided sales flow.", icon: ShieldCheck },
  { title: "Human approval", text: "Review drafts, safety flags, and context before responses reach the customer.", icon: UserCheck },
  { title: "Qualified leads", text: "Convert approved conversations into clear opportunities for the sales team.", icon: Sparkles }
];

export function App() {
  return (
    <main className="min-h-screen bg-cloud text-ink">
      <section className="relative overflow-hidden bg-ink text-white">
        <img className="absolute inset-0 h-full w-full object-cover opacity-35" src={heroImage} alt="" />
        <div className="relative mx-auto grid min-h-[86vh] max-w-7xl content-center gap-10 px-5 py-16 md:grid-cols-[1.05fr_0.95fr] md:px-8">
          <div className="max-w-3xl">
            <p className="mb-4 text-sm font-semibold uppercase tracking-[0.18em] text-gold">Consent-first automation</p>
            <h1 className="text-4xl font-semibold leading-tight md:text-6xl">Ethical Dialogue AI</h1>
            <p className="mt-5 max-w-2xl text-lg leading-8 text-slate-100">
              Turn Telegram product conversations into approved responses and qualified leads while keeping consent, safety, and human review at the center.
            </p>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <a className="inline-flex items-center justify-center gap-2 rounded-md bg-gold px-5 py-3 font-semibold text-ink" href={adminUrl}>
                Sign in <ArrowRight size={18} />
              </a>
              <a className="inline-flex items-center justify-center rounded-md border border-white/35 px-5 py-3 font-semibold text-white" href="#workflow">
                See workflow
              </a>
            </div>
          </div>
          <div className="self-end rounded-md border border-white/20 bg-white/10 p-5 backdrop-blur">
            <p className="text-sm font-medium text-gold">Operator snapshot</p>
            <div className="mt-4 grid gap-3">
              {["12 conversations analyzed", "7 drafts awaiting approval", "4 consent grants captured"].map((item) => (
                <div key={item} className="flex items-center gap-3 rounded-md bg-white/10 px-4 py-3">
                  <CheckCircle2 size={18} className="text-gold" />
                  <span>{item}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section id="workflow" className="mx-auto max-w-7xl px-5 py-16 md:px-8">
        <div className="max-w-2xl">
          <p className="text-sm font-semibold uppercase text-coral">Workflow</p>
          <h2 className="mt-2 text-3xl font-semibold">From conversation to qualified lead</h2>
        </div>
        <div className="mt-8 grid gap-4 md:grid-cols-4">
          {workflow.map((item) => (
            <article key={item.title} className="rounded-md border border-line bg-white p-5">
              <item.icon className="text-moss" size={24} />
              <h3 className="mt-4 font-semibold">{item.title}</h3>
              <p className="mt-2 text-sm leading-6 text-slate-600">{item.text}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="border-y border-line bg-white">
        <div className="mx-auto grid max-w-7xl gap-8 px-5 py-16 md:grid-cols-3 md:px-8">
          <div>
            <p className="text-sm font-semibold uppercase text-coral">Trust</p>
            <h2 className="mt-2 text-3xl font-semibold">Built for careful teams</h2>
          </div>
          <div className="md:col-span-2 grid gap-4 sm:grid-cols-3">
            {["Consent records", "Audit history", "No secret exposure"].map((item) => (
              <div key={item} className="rounded-md bg-cloud p-5 font-medium">{item}</div>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-5 py-16 md:px-8">
        <div className="rounded-md bg-moss px-6 py-10 text-white md:px-10">
          <h2 className="text-3xl font-semibold">Run the workflow from one focused dashboard.</h2>
          <p className="mt-3 max-w-2xl text-white/80">Review approvals, monitor integrations, convert leads, and keep every AI-assisted conversation accountable.</p>
          <a className="mt-6 inline-flex items-center gap-2 rounded-md bg-white px-5 py-3 font-semibold text-moss" href={adminUrl}>
            Sign in <ArrowRight size={18} />
          </a>
        </div>
      </section>
    </main>
  );
}
```

Create `landing/src/styles.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  color: #16211f;
  background: #f4f7f4;
}

body {
  margin: 0;
}

a {
  text-decoration: none;
}
```

- [ ] **Step 6: Run the landing test to verify it passes**

Run:

```bash
cd landing && npm test
```

Expected: PASS.

- [ ] **Step 7: Run the landing build**

Run:

```bash
cd landing && npm run build
```

Expected: PASS.

- [ ] **Step 8: Commit Task 3**

```bash
git add landing
git commit -m "feat: add separate landing app"
```

---

### Task 4: Documentation and Full Verification

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: Admin and landing app scripts.
- Produces: README commands for running both projects.

- [ ] **Step 1: Update README with separate app commands**

Add this section to `README.md`:

````md
## Frontend Apps

This repo contains two independent frontend apps.

### Admin Dashboard

```bash
cd frontend
npm install
npm run dev
```

The admin dashboard runs on `http://localhost:5173` and contains the authenticated workspace dashboard plus the staff-only `/app/superadmin` area.

### Landing Page

```bash
cd landing
npm install
npm run dev
```

The landing page runs on `http://localhost:5174`. Set `VITE_ADMIN_URL` when the landing app should link to a deployed admin dashboard instead of the local `/signin` path.
````

- [ ] **Step 2: Run admin tests**

Run:

```bash
cd frontend && npm test
```

Expected: PASS.

- [ ] **Step 3: Run admin build**

Run:

```bash
cd frontend && npm run build
```

Expected: PASS.

- [ ] **Step 4: Run landing tests**

Run:

```bash
cd landing && npm test
```

Expected: PASS.

- [ ] **Step 5: Run landing build**

Run:

```bash
cd landing && npm run build
```

Expected: PASS.

- [ ] **Step 6: Check git status**

Run:

```bash
git status --short --branch
```

Expected: only README changes before the commit.

- [ ] **Step 7: Commit Task 4**

```bash
git add README.md
git commit -m "docs: document frontend app commands"
```

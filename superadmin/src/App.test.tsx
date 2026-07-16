import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";

import { AppRoutes } from "./App";
import { api, tokenStore } from "./services/api";

vi.mock("./services/api", async () => {
  const actual = await vi.importActual<typeof import("./services/api")>("./services/api");
  return {
    ...actual,
    tokenStore: {
      access: null,
      set: vi.fn(),
      clear: vi.fn()
    },
    api: {
      login: vi.fn(),
      me: vi.fn(),
      overview: vi.fn(),
      workspaces: vi.fn(),
      users: vi.fn(),
      integrations: vi.fn(),
      events: vi.fn()
    }
  };
});

function renderApp(path = "/signin") {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[path]}>
        <AppRoutes />
      </MemoryRouter>
    </QueryClientProvider>
  );
}

beforeEach(() => {
  vi.clearAllMocks();
});

afterEach(() => {
  cleanup();
});

describe("Superadmin app", () => {
  test("renders Uzbek sign-in labels and calls login", async () => {
    vi.mocked(api.login).mockResolvedValue({ access: "access", refresh: "refresh" });
    vi.mocked(api.me).mockResolvedValue({ user: { id: "1", email: "staff@example.com", full_name: "Staff", is_staff: true, is_superuser: false }, memberships: [] });

    renderApp("/signin");

    await userEvent.clear(screen.getByLabelText("Email"));
    await userEvent.type(screen.getByLabelText("Email"), "staff@example.com");
    await userEvent.clear(screen.getByLabelText("Parol"));
    await userEvent.type(screen.getByLabelText("Parol"), "ChangeMe123!");
    await userEvent.click(screen.getByRole("button", { name: "Kirish" }));

    expect(api.login).toHaveBeenCalledWith("staff@example.com", "ChangeMe123!");
    expect(tokenStore.set).toHaveBeenCalledWith("access", "refresh");
  });

  test("renders Uzbek platform dashboard for staff users", async () => {
    vi.mocked(tokenStore).access = "token";
    vi.mocked(api.me).mockResolvedValue({ user: { id: "1", email: "staff@example.com", full_name: "Staff", is_staff: true, is_superuser: false }, memberships: [] });
    vi.mocked(api.overview).mockResolvedValue({ users: 7, active_workspaces: 2, opportunities: 11, consent_grants: 5, leads: 4, telegram_connections: 1 });
    vi.mocked(api.integrations).mockResolvedValue({
      ai: { provider: "mock", model: "gemini-2.5-flash", credential_configured: true, vertex_project_configured: false },
      telegram: { provider: "mock", bot_token_configured: false, webhook_secret_configured: true, webhook_base_url_configured: true }
    });
    vi.mocked(api.workspaces).mockResolvedValue({ count: 1, next: null, previous: null, results: [{ id: "w1", name: "Northwind", business_name: "Northwind", industry: "Retail", is_active: true, owner: "owner@example.com", member_count: 2, lead_count: 3, plan: "Growth" }] });
    vi.mocked(api.users).mockResolvedValue({ count: 1, next: null, previous: null, results: [{ id: "u1", email: "owner@example.com", full_name: "Owner", membership_count: 1, is_staff: false, is_superuser: false, last_login: null }] });
    vi.mocked(api.events).mockResolvedValue({ count: 1, next: null, previous: null, results: [{ id: "e1", source: "audit_log", workspace: "Northwind", created_at: "2026-07-16T10:00:00Z", summary: "lead.created" }] });

    renderApp("/app");

    expect(await screen.findByText("Platforma boshqaruvi")).toBeInTheDocument();
    expect(await screen.findByText("Foydalanuvchilar")).toBeInTheDocument();
    expect(await screen.findByText("Ish joylari")).toBeInTheDocument();
    expect(await screen.findByText("So'nggi hodisalar")).toBeInTheDocument();
  });

  test("blocks non-staff users in Uzbek and avoids superadmin fetches", async () => {
    vi.mocked(tokenStore).access = "token";
    vi.mocked(api.me).mockResolvedValue({ user: { id: "2", email: "owner@example.com", full_name: "Owner", is_staff: false, is_superuser: false }, memberships: [] });

    renderApp("/app");

    expect(await screen.findByText("Ruxsat yo'q")).toBeInTheDocument();
    expect(api.overview).not.toHaveBeenCalled();
  });
});

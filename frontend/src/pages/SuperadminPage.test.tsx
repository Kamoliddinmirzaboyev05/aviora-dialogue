import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";

import { SuperadminPage } from "./SuperadminPage";
import { useAuth } from "../features/auth/AuthProvider";
import { api } from "../services/api";

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

beforeEach(() => {
  vi.clearAllMocks();
});

afterEach(() => {
  cleanup();
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
    expect((await screen.findAllByText("owner@example.com")).length).toBeGreaterThan(0);
    expect(await screen.findByText("AI classify_message request failed.")).toBeInTheDocument();
    expect(screen.getAllByText("mock").length).toBeGreaterThan(0);
  });

  test("renders access denied for non-staff users", () => {
    renderPage(false);

    expect(screen.getByText("Access denied")).toBeInTheDocument();
    expect(api.superadminOverview).not.toHaveBeenCalled();
  });
});

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { cleanup, render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";

import { AuthProvider } from "../features/auth/AuthProvider";
import { api } from "../services/api";
import { DashboardLayout } from "./DashboardLayout";

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

beforeEach(() => {
  vi.clearAllMocks();
});

afterEach(() => {
  cleanup();
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

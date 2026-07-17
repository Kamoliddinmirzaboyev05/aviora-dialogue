import type { IntegrationStatus, MeResponse, Paginated, PlatformEvent, PlatformOverview, PlatformUser, PlatformWorkspace } from "../types/api";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ??
  (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
    ? "http://localhost:8000/api/v1"
    : "/api/v1");

type LoginResponse = {
  access: string;
  refresh: string;
};

export const tokenStore = {
  get access() {
    return localStorage.getItem("superadminAccessToken");
  },
  set(access: string, refresh: string) {
    localStorage.setItem("superadminAccessToken", access);
    localStorage.setItem("superadminRefreshToken", refresh);
  },
  clear() {
    localStorage.removeItem("superadminAccessToken");
    localStorage.removeItem("superadminRefreshToken");
  }
};

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");
  if (tokenStore.access) {
    headers.set("Authorization", `Bearer ${tokenStore.access}`);
  }
  const response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: { message: response.statusText } }));
    throw new Error(error.error?.message ?? "So'rov bajarilmadi");
  }
  return response.json() as Promise<T>;
}

function searchParam(search?: string) {
  const trimmed = search?.trim();
  return trimmed ? `?search=${encodeURIComponent(trimmed)}` : "";
}

export const api = {
  login: (email: string, password: string) =>
    request<LoginResponse>("/auth/login/", {
      method: "POST",
      body: JSON.stringify({ email, password })
    }),
  me: () => request<MeResponse>("/auth/me/"),
  overview: () => request<PlatformOverview>("/superadmin/overview/"),
  workspaces: (search?: string) => request<Paginated<PlatformWorkspace>>(`/superadmin/workspaces/${searchParam(search)}`),
  users: (search?: string) => request<Paginated<PlatformUser>>(`/superadmin/users/${searchParam(search)}`),
  integrations: () => request<IntegrationStatus>("/superadmin/integrations/"),
  events: () => request<Paginated<PlatformEvent>>("/superadmin/events/")
};

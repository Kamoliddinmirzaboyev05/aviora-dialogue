import type {
  Analytics,
  Conversation,
  Draft,
  Lead,
  MeResponse,
  Opportunity,
  Paginated,
  Workspace
} from "../types/api";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ??
  (import.meta.env.DEV ? "http://localhost:8000/api/v1" : "https://dialogapi.webportfolio.uz/api/v1");

type LoginResponse = {
  access: string;
  refresh: string;
};

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export const tokenStore = {
  get access() {
    return localStorage.getItem("accessToken");
  },
  set(access: string, refresh: string) {
    localStorage.setItem("accessToken", access);
    localStorage.setItem("refreshToken", refresh);
  },
  clear() {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");
  }
};

function extractError(body: unknown, fallback: string): string {
  if (!body || typeof body !== "object") return fallback;
  const b = body as Record<string, unknown>;
  if (b.error && typeof b.error === "object" && "message" in b.error) return String((b.error as { message: unknown }).message);
  if (typeof b.detail === "string") return b.detail;
  const first = Object.values(b).find((v) => (Array.isArray(v) && v.length) || typeof v === "string");
  if (Array.isArray(first)) return String(first[0]);
  if (typeof first === "string") return first;
  return fallback;
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");
  if (tokenStore.access) {
    headers.set("Authorization", `Bearer ${tokenStore.access}`);
  }
  const response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new ApiError(response.status, extractError(error, "So'rov bajarilmadi"));
  }
  return response.json() as Promise<T>;
}

export const api = {
  login: async (email: string, password: string) => {
    const result = await request<LoginResponse>("/auth/login/", {
      method: "POST",
      body: JSON.stringify({ email, password })
    });
    tokenStore.set(result.access, result.refresh);
    return result;
  },
  me: () => request<MeResponse>("/auth/me/"),
  workspaces: () => request<Paginated<Workspace>>("/workspaces/"),
  analytics: (workspace: string) => request<Analytics>(`/analytics/overview/?workspace=${workspace}`),
  opportunities: () => request<Paginated<Opportunity>>("/opportunities/"),
  approvals: () => request<Paginated<Draft>>("/approvals/"),
  conversations: () => request<Paginated<Conversation>>("/conversations/"),
  leads: () => request<Paginated<Lead>>("/leads/"),
  products: () => request<Paginated<Record<string, unknown>>>("/products/"),
  triggers: () => request<Paginated<Record<string, unknown>>>("/triggers/"),
  telegramConnections: (workspace: string) => request<{ results: Record<string, unknown>[] }>(`/telegram/connections/?workspace=${workspace}`),
  telegramChats: (workspace: string) => request<{ results: Record<string, unknown>[] }>(`/telegram/chats/?workspace=${workspace}`),
  simulateMessage: (workspace: string, message: string) =>
    request<{ opportunity: Opportunity; draft: Draft }>("/telegram/simulate-message/", {
      method: "POST",
      body: JSON.stringify({ workspace, message, sender_name: "Alex Founder", telegram_user_id: `demo-${Date.now()}` })
    }),
  approveDraft: (draftId: string) =>
    request<{ draft: Draft; conversation: { id: string; consent_status: string } }>(`/approvals/${draftId}/approve/`, { method: "POST", body: "{}" }),
  simulateConsent: (conversationId: string, message: string) =>
    request<{ consent: { status: string } }>(`/conversations/${conversationId}/simulate-consent/`, {
      method: "POST",
      body: JSON.stringify({ message })
    }),
  generateProductResponse: (conversationId: string) =>
    request<{ message: Conversation["messages"][number] }>(`/conversations/${conversationId}/generate-product-response/`, { method: "POST", body: "{}" }),
  convertLead: (workspace: string, conversation: string) =>
    request<Lead>("/leads/convert/", {
      method: "POST",
      body: JSON.stringify({ workspace, conversation })
    }),
  updateLead: (leadId: string, status: string) =>
    request<Lead>(`/leads/${leadId}/`, {
      method: "PATCH",
      body: JSON.stringify({ status })
    }),
  changePassword: (oldPassword: string, newPassword: string) =>
    request<{ detail: string }>("/auth/change-password/", {
      method: "POST",
      body: JSON.stringify({ old_password: oldPassword, new_password: newPassword })
    })
};

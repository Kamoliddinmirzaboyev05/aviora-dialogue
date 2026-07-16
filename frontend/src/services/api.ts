import type { Analytics, Conversation, Draft, Lead, MeResponse, Opportunity, Paginated, Workspace } from "../types/api";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

type LoginResponse = {
  access: string;
  refresh: string;
};

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

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");
  if (tokenStore.access) {
    headers.set("Authorization", `Bearer ${tokenStore.access}`);
  }
  const response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: { message: response.statusText } }));
    throw new Error(error.error?.message ?? "Request failed");
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
    })
};

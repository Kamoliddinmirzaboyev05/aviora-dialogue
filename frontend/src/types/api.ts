export type Workspace = {
  id: string;
  name: string;
  slug: string;
  business_name: string;
};

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

export type Paginated<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

export type Opportunity = {
  id: string;
  workspace: string;
  chat_title: string;
  contact_name: string;
  product_name: string;
  source_message: string;
  detected_intent: string;
  relevance_score: number;
  confidence: number;
  concise_reason: string;
  status: string;
  created_at: string;
};

export type Draft = {
  id: string;
  text: string;
  status: string;
  safety_flags: string[];
  opportunity: Opportunity;
};

export type Conversation = {
  id: string;
  contact_name: string;
  chat_title: string;
  product_name: string;
  consent_status: string;
  status: string;
  summary: string;
  messages: Array<{ id: string; direction: string; body: string; source: string; delivery_state: string; created_at: string }>;
};

export type Lead = {
  id: string;
  contact_name: string;
  product_name: string;
  detected_need: string;
  score: number;
  status: string;
  created_at: string;
};

export type Analytics = {
  messages_analyzed: number;
  opportunities: number;
  pending_approvals: number;
  permission_requests_sent: number;
  consent_granted: number;
  leads: number;
  conversion_rate: number;
};

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

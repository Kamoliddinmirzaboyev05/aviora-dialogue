export type UserIdentity = {
  id: string;
  email: string;
  full_name: string;
  is_staff: boolean;
  is_superuser: boolean;
};

export type MeResponse = {
  user: UserIdentity;
  memberships: unknown[];
};

export type Paginated<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

export type PlatformOverview = {
  users: number;
  active_workspaces: number;
  opportunities: number;
  consent_grants: number;
  leads: number;
  telegram_connections: number;
};

export type PlatformWorkspace = {
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

export type PlatformUser = {
  id: string;
  email: string;
  full_name: string;
  membership_count: number;
  is_staff: boolean;
  is_superuser: boolean;
  last_login: string | null;
};

export type IntegrationStatus = {
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

export type PlatformEvent = {
  id: string;
  source: string;
  workspace: string;
  created_at: string;
  summary: string;
};

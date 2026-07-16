export type Workspace = {
  id: string;
  name: string;
  slug: string;
  business_name: string;
};

export type MeResponse = {
  user: { id: string; email: string; full_name: string };
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

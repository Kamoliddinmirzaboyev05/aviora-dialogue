import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, CheckCircle2, Search, ShieldCheck, XCircle } from "lucide-react";

import { Badge } from "../components/ui/Badge";
import { Card } from "../components/ui/Card";
import { useAuth } from "../features/auth/AuthProvider";
import { api } from "../services/api";
import type { SuperadminOverview } from "../types/api";

const metricLabels: Array<{ key: keyof SuperadminOverview; label: string }> = [
  { key: "users", label: "Users" },
  { key: "active_workspaces", label: "Active workspaces" },
  { key: "opportunities", label: "Opportunities" },
  { key: "consent_grants", label: "Consent grants" },
  { key: "leads", label: "Leads" },
  { key: "telegram_connections", label: "Telegram connections" }
];

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
          metricLabels.map((metric) => (
            <Card key={metric.key}>
              <p className="text-xs font-medium uppercase text-slate-500">{metric.label}</p>
              <p className="mt-2 text-2xl font-semibold">{overview.data[metric.key]}</p>
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
              <div className="flex justify-between gap-4">
                <dt className="text-slate-500">Provider</dt>
                <dd>{integrations.data.ai.provider}</dd>
              </div>
              <div className="flex justify-between gap-4">
                <dt className="text-slate-500">Model</dt>
                <dd>{integrations.data.ai.model}</dd>
              </div>
              <div className="flex justify-between gap-4">
                <dt className="text-slate-500">Credential</dt>
                <dd><StatusMark ok={integrations.data.ai.credential_configured} /></dd>
              </div>
              <div className="flex justify-between gap-4">
                <dt className="text-slate-500">Vertex project</dt>
                <dd><StatusMark ok={integrations.data.ai.vertex_project_configured} /></dd>
              </div>
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
              <div className="flex justify-between gap-4">
                <dt className="text-slate-500">Provider</dt>
                <dd>{integrations.data.telegram.provider}</dd>
              </div>
              <div className="flex justify-between gap-4">
                <dt className="text-slate-500">Bot token</dt>
                <dd><StatusMark ok={integrations.data.telegram.bot_token_configured} /></dd>
              </div>
              <div className="flex justify-between gap-4">
                <dt className="text-slate-500">Webhook secret</dt>
                <dd><StatusMark ok={integrations.data.telegram.webhook_secret_configured} /></dd>
              </div>
              <div className="flex justify-between gap-4">
                <dt className="text-slate-500">Webhook URL</dt>
                <dd><StatusMark ok={integrations.data.telegram.webhook_base_url_configured} /></dd>
              </div>
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
                      <td className="py-3">
                        <p className="font-medium">{workspace.name}</p>
                        <p className="text-xs text-slate-500">{workspace.business_name} - {workspace.industry}</p>
                      </td>
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
                  <p className="text-sm text-slate-500">{event.workspace} - {event.source}</p>
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

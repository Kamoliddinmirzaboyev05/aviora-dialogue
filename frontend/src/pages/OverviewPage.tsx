import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { CheckCircle2, MessageSquare, Target, Users } from "lucide-react";

import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Card, CardTitle } from "../components/ui/Card";
import { api } from "../services/api";
import { useAuth } from "../features/auth/AuthProvider";

export function OverviewPage() {
  const { workspace } = useAuth();
  const analytics = useQuery({ queryKey: ["analytics", workspace?.id], queryFn: () => api.analytics(workspace!.id), enabled: Boolean(workspace) });

  const stats = [
    { label: "Messages analyzed", value: analytics.data?.messages_analyzed ?? 0, icon: MessageSquare },
    { label: "Opportunities", value: analytics.data?.opportunities ?? 0, icon: Target },
    { label: "Consent granted", value: analytics.data?.consent_granted ?? 0, icon: CheckCircle2 },
    { label: "Leads", value: analytics.data?.leads ?? 0, icon: Users }
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-3 md:flex-row md:items-center">
        <div>
          <h1 className="text-2xl font-semibold">Overview</h1>
          <p className="text-sm text-slate-600">Operational snapshot for {workspace?.name}</p>
        </div>
        <Link to="/app/simulator"><Button>Run simulator</Button></Link>
      </div>
      <div className="grid gap-4 md:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.label}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-500">{stat.label}</p>
                <p className="mt-2 text-2xl font-semibold">{stat.value}</p>
              </div>
              <stat.icon className="text-teal" size={24} />
            </div>
          </Card>
        ))}
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardTitle>Setup checklist</CardTitle>
          <div className="mt-4 space-y-3 text-sm">
            {["Mock Telegram connection", "SalesPilot CRM product", "CRM trigger set", "Manual approval mode"].map((item) => (
              <div key={item} className="flex items-center justify-between rounded-md border border-line px-3 py-2">
                <span>{item}</span>
                <Badge tone="green">ready</Badge>
              </div>
            ))}
          </div>
        </Card>
        <Card>
          <CardTitle>Health</CardTitle>
          <div className="mt-4 grid gap-3 text-sm md:grid-cols-2">
            {["Backend API", "Database", "Mock Telegram", "Mock AI", "Consent engine", "Approval queue"].map((item) => (
              <div key={item} className="rounded-md bg-panel px-3 py-2">
                <span className="font-medium">{item}</span>
                <p className="text-xs text-emerald-700">available</p>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}

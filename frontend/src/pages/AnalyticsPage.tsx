import { useQuery } from "@tanstack/react-query";
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { Card, CardTitle } from "../components/ui/Card";
import { api } from "../services/api";
import { useAuth } from "../features/auth/AuthProvider";

export function AnalyticsPage() {
  const { workspace } = useAuth();
  const analytics = useQuery({ queryKey: ["analytics", workspace?.id], queryFn: () => api.analytics(workspace!.id), enabled: Boolean(workspace) });
  const data = analytics.data
    ? [
        { name: "Opportunities", value: analytics.data.opportunities },
        { name: "Consent", value: analytics.data.consent_granted },
        { name: "Leads", value: analytics.data.leads }
      ]
    : [];
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Analytics</h1>
      <Card>
        <CardTitle>Consent funnel</CardTitle>
        <div className="mt-4 h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data}>
              <XAxis dataKey="name" />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="value" fill="#0f766e" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>
    </div>
  );
}

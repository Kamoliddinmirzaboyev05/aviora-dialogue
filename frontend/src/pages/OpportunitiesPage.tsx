import { useQuery } from "@tanstack/react-query";

import { Badge } from "../components/ui/Badge";
import { Card } from "../components/ui/Card";
import { EmptyState } from "../components/ui/EmptyState";
import { api } from "../services/api";

export function OpportunitiesPage() {
  const opportunities = useQuery({ queryKey: ["opportunities"], queryFn: api.opportunities });
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Opportunities</h1>
      {!opportunities.data?.results.length && <EmptyState title="No opportunities yet. Run the simulator to create one." />}
      <div className="space-y-3">
        {opportunities.data?.results.map((item) => (
          <Card key={item.id}>
            <div className="flex flex-col justify-between gap-3 md:flex-row">
              <div>
                <h2 className="font-semibold">{item.contact_name}</h2>
                <p className="text-sm text-slate-600">{item.source_message}</p>
                <p className="mt-2 text-sm">{item.concise_reason}</p>
              </div>
              <div className="flex gap-2"><Badge>{item.status}</Badge><Badge tone="green">{item.relevance_score}</Badge></div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}

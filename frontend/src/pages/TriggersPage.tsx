import { useQuery } from "@tanstack/react-query";

import { Badge } from "../components/ui/Badge";
import { Card } from "../components/ui/Card";
import { api } from "../services/api";

export function TriggersPage() {
  const triggers = useQuery({ queryKey: ["triggers"], queryFn: api.triggers });
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Triggers</h1>
      <div className="space-y-3">
        {triggers.data?.results.map((trigger) => (
          <Card key={String(trigger.id)}>
            <div className="flex items-center justify-between">
              <div>
                <h2 className="font-semibold">{String(trigger.name)}</h2>
                <p className="text-sm text-slate-600">{String(trigger.description)}</p>
              </div>
              <Badge tone="green">{String(trigger.minimum_score)}</Badge>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}

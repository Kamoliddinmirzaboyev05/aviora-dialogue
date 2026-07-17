import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Card, CardTitle } from "../components/ui/Card";
import { EmptyState } from "../components/ui/EmptyState";
import { api } from "../services/api";
import { draftStatusLabels, statusLabel } from "../lib/statusLabels";

export function ApprovalsPage() {
  const queryClient = useQueryClient();
  const approvals = useQuery({ queryKey: ["approvals"], queryFn: api.approvals });
  const approve = useMutation({
    mutationFn: api.approveDraft,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["approvals"] });
      queryClient.invalidateQueries({ queryKey: ["conversations"] });
      queryClient.invalidateQueries({ queryKey: ["analytics"] });
    }
  });

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Tasdiqlash navbati</h1>
      {!approvals.data?.results.length && <EmptyState title="Ko'rib chiqish uchun qoralamalar yo'q." />}
      <div className="space-y-4">
        {approvals.data?.results.map((draft) => (
          <Card key={draft.id}>
            <div className="flex flex-col justify-between gap-4 lg:flex-row">
              <div className="space-y-2">
                <CardTitle>{draft.opportunity.contact_name}</CardTitle>
                <p className="text-sm text-slate-600">{draft.opportunity.source_message}</p>
                <div className="rounded-md bg-panel p-4 text-sm">{draft.text}</div>
                <div className="flex gap-2"><Badge tone="amber">{statusLabel(draftStatusLabels, draft.status)}</Badge><Badge>{draft.opportunity.relevance_score}</Badge></div>
              </div>
              <div className="flex min-w-52 items-start gap-2">
                {draft.status === "draft" ? <Button onClick={() => approve.mutate(draft.id)} disabled={approve.isPending}>Tasdiqlash</Button> : <Link to="/app/conversations"><Button variant="secondary">Suhbat</Button></Link>}
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}

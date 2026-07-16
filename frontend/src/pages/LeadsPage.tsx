import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { EmptyState } from "../components/ui/EmptyState";
import { api } from "../services/api";
import { useAuth } from "../features/auth/AuthProvider";

export function LeadsPage() {
  const { workspace } = useAuth();
  const queryClient = useQueryClient();
  const leads = useQuery({ queryKey: ["leads"], queryFn: api.leads });
  const conversations = useQuery({ queryKey: ["conversations"], queryFn: api.conversations });
  const convert = useMutation({
    mutationFn: (conversation: string) => api.convertLead(workspace!.id, conversation),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["leads"] });
      queryClient.invalidateQueries({ queryKey: ["analytics"] });
    }
  });
  const update = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) => api.updateLead(id, status),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["leads"] })
  });

  const convertible = conversations.data?.results.find((conversation) => conversation.consent_status === "granted");

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-3 md:flex-row md:items-center">
        <h1 className="text-2xl font-semibold">Leads</h1>
        <Button disabled={!convertible || convert.isPending} onClick={() => convertible && convert.mutate(convertible.id)}>Convert latest consent</Button>
      </div>
      {!leads.data?.results.length && <EmptyState title="No leads yet. Grant consent in a conversation, then convert it." />}
      <div className="grid gap-4 lg:grid-cols-3">
        {leads.data?.results.map((lead) => (
          <Card key={lead.id}>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h2 className="font-semibold">{lead.contact_name}</h2>
                <Badge tone="green">{lead.score}</Badge>
              </div>
              <p className="text-sm text-slate-600">{lead.detected_need}</p>
              <select className="focus-ring w-full rounded-md border border-line px-3 py-2 text-sm" value={lead.status} onChange={(event) => update.mutate({ id: lead.id, status: event.target.value })}>
                {["new", "qualified", "contacted", "meeting_scheduled", "won", "lost"].map((status) => <option key={status} value={status}>{status}</option>)}
              </select>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}

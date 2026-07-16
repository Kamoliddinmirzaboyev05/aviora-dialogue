import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Card, CardTitle } from "../components/ui/Card";
import { EmptyState } from "../components/ui/EmptyState";
import { api } from "../services/api";

export function ConversationsPage() {
  const queryClient = useQueryClient();
  const conversations = useQuery({ queryKey: ["conversations"], queryFn: api.conversations });
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const selected = conversations.data?.results.find((conversation) => conversation.id === (selectedId ?? conversations.data?.results[0]?.id));
  const consent = useMutation({
    mutationFn: (id: string) => api.simulateConsent(id, "Yes, please send me more information."),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["conversations"] })
  });
  const generate = useMutation({
    mutationFn: api.generateProductResponse,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["conversations"] })
  });

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Conversations</h1>
      {!conversations.data?.results.length && <EmptyState title="Approve a permission request to start a conversation." />}
      <div className="grid gap-4 lg:grid-cols-[320px_1fr]">
        <div className="space-y-2">
          {conversations.data?.results.map((conversation) => (
            <button key={conversation.id} className="focus-ring w-full rounded-md border border-line bg-white p-3 text-left text-sm" onClick={() => setSelectedId(conversation.id)}>
              <span className="font-medium">{conversation.contact_name}</span>
              <p className="text-xs text-slate-500">{conversation.consent_status}</p>
            </button>
          ))}
        </div>
        {selected && (
          <Card>
            <div className="mb-4 flex flex-col justify-between gap-3 md:flex-row md:items-center">
              <div>
                <CardTitle>{selected.contact_name}</CardTitle>
                <p className="text-sm text-slate-600">{selected.chat_title} · {selected.product_name}</p>
              </div>
              <Badge tone={selected.consent_status === "granted" ? "green" : "amber"}>{selected.consent_status}</Badge>
            </div>
            <div className="space-y-3">
              {selected.messages.map((message) => (
                <div key={message.id} className={`max-w-2xl rounded-md p-3 text-sm ${message.direction === "outbound" ? "ml-auto bg-teal text-white" : "bg-panel text-ink"}`}>
                  <p>{message.body}</p>
                  <span className="mt-1 block text-xs opacity-75">{message.source} · {message.delivery_state}</span>
                </div>
              ))}
            </div>
            <div className="mt-5 flex flex-wrap gap-2">
              <Button variant="secondary" onClick={() => consent.mutate(selected.id)} disabled={consent.isPending || selected.consent_status === "granted"}>Simulate consent</Button>
              <Button onClick={() => generate.mutate(selected.id)} disabled={generate.isPending || selected.consent_status !== "granted"}>Generate response</Button>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}

import { FormEvent, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Card, CardTitle } from "../components/ui/Card";
import { api } from "../services/api";
import { useAuth } from "../features/auth/AuthProvider";

export function SimulatorPage() {
  const { workspace } = useAuth();
  const queryClient = useQueryClient();
  const [message, setMessage] = useState("Kichik savdo jamoasi uchun oddiy CRM tavsiya qila oladigan bormi?");
  const simulation = useMutation({
    mutationFn: () => api.simulateMessage(workspace!.id, message),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["opportunities"] });
      queryClient.invalidateQueries({ queryKey: ["approvals"] });
      queryClient.invalidateQueries({ queryKey: ["analytics"] });
    }
  });

  function submit(event: FormEvent) {
    event.preventDefault();
    simulation.mutate();
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">AI Simulyator</h1>
        <p className="text-sm text-slate-600">Soxta Telegram xabarini xuddi shu backend jarayoni orqali qayta ishlang.</p>
      </div>
      <Card>
        <form onSubmit={submit} className="space-y-4">
          <label className="block text-sm font-medium">
            Kelayotgan Telegram xabari
            <textarea className="focus-ring mt-2 min-h-28 w-full rounded-md border border-line px-3 py-2" value={message} onChange={(event) => setMessage(event.target.value)} />
          </label>
          <Button disabled={simulation.isPending}>Xabarni tahlil qilish</Button>
        </form>
      </Card>
      {simulation.data && (
        <Card>
          <CardTitle>Natija</CardTitle>
          <div className="mt-4 space-y-3 text-sm">
            <p><Badge tone="green">imkoniyat yaratildi</Badge></p>
            <p className="font-medium">{simulation.data.opportunity.concise_reason}</p>
            <div className="rounded-md bg-panel p-4">{simulation.data.draft.text}</div>
            <Link to="/app/approvals"><Button variant="secondary">Tasdiqlash navbatini ochish</Button></Link>
          </div>
        </Card>
      )}
    </div>
  );
}

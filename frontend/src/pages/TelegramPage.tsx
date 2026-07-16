import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Card, CardTitle } from "../components/ui/Card";
import { api } from "../services/api";
import { useAuth } from "../features/auth/AuthProvider";

export function TelegramPage() {
  const { workspace } = useAuth();
  const connections = useQuery({ queryKey: ["telegram-connections", workspace?.id], queryFn: () => api.telegramConnections(workspace!.id), enabled: Boolean(workspace) });
  const chats = useQuery({ queryKey: ["telegram-chats", workspace?.id], queryFn: () => api.telegramChats(workspace!.id), enabled: Boolean(workspace) });
  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-3 md:flex-row md:items-center">
        <h1 className="text-2xl font-semibold">Telegram</h1>
        <Link to="/app/simulator"><Button>Simulate message</Button></Link>
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardTitle>Connection</CardTitle>
          <div className="mt-4 space-y-3">
            {connections.data?.results.map((connection) => (
              <div key={String(connection.id)} className="rounded-md bg-panel p-3 text-sm">
                <p className="font-medium">{String(connection.name)}</p>
                <p className="text-slate-600">@{String(connection.bot_username)}</p>
                <Badge tone="green">{String(connection.webhook_status)}</Badge>
              </div>
            ))}
          </div>
        </Card>
        <Card>
          <CardTitle>Monitored chats</CardTitle>
          <div className="mt-4 space-y-3">
            {chats.data?.results.map((chat) => (
              <div key={String(chat.id)} className="rounded-md bg-panel p-3 text-sm">
                <p className="font-medium">{String(chat.title)}</p>
                <p className="text-slate-600">{String(chat.telegram_chat_id)}</p>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}

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
    { label: "Tahlil qilingan xabarlar", value: analytics.data?.messages_analyzed ?? 0, icon: MessageSquare },
    { label: "Imkoniyatlar", value: analytics.data?.opportunities ?? 0, icon: Target },
    { label: "Rozilik berilgan", value: analytics.data?.consent_granted ?? 0, icon: CheckCircle2 },
    { label: "Lidlar", value: analytics.data?.leads ?? 0, icon: Users }
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-3 md:flex-row md:items-center">
        <div>
          <h1 className="text-2xl font-semibold">Umumiy ko'rinish</h1>
          <p className="text-sm text-slate-600">{workspace?.name} uchun operatsion holat</p>
        </div>
        <Link to="/app/simulator"><Button>Simulyatorni ishga tushirish</Button></Link>
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
          <CardTitle>Sozlash ro'yxati</CardTitle>
          <div className="mt-4 space-y-3 text-sm">
            {["Soxta Telegram ulanishi", "SalesPilot CRM mahsuloti", "CRM trigger o'rnatilgan", "Qo'lda tasdiqlash rejimi"].map((item) => (
              <div key={item} className="flex items-center justify-between rounded-md border border-line px-3 py-2">
                <span>{item}</span>
                <Badge tone="green">tayyor</Badge>
              </div>
            ))}
          </div>
        </Card>
        <Card>
          <CardTitle>Holat</CardTitle>
          <div className="mt-4 grid gap-3 text-sm md:grid-cols-2">
            {["Backend API", "Ma'lumotlar bazasi", "Soxta Telegram", "Soxta AI", "Rozilik mexanizmi", "Tasdiqlash navbati"].map((item) => (
              <div key={item} className="rounded-md bg-panel px-3 py-2">
                <span className="font-medium">{item}</span>
                <p className="text-xs text-emerald-700">mavjud</p>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}

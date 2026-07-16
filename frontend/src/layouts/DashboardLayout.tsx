import { NavLink, Outlet, Navigate } from "react-router-dom";
import { Activity, Bot, CheckSquare, LineChart, MessageSquare, Package, Radio, Settings, ShieldCheck, Target, Users } from "lucide-react";

import { Button } from "../components/ui/Button";
import { useAuth } from "../features/auth/AuthProvider";

const nav = [
  { to: "/app", label: "Overview", icon: Activity },
  { to: "/app/telegram", label: "Telegram", icon: Radio },
  { to: "/app/simulator", label: "Simulator", icon: Bot },
  { to: "/app/opportunities", label: "Opportunities", icon: Target },
  { to: "/app/approvals", label: "Approval Queue", icon: CheckSquare },
  { to: "/app/conversations", label: "Conversations", icon: MessageSquare },
  { to: "/app/leads", label: "Leads", icon: Users },
  { to: "/app/products", label: "Products", icon: Package },
  { to: "/app/triggers", label: "Triggers", icon: Settings },
  { to: "/app/analytics", label: "Analytics", icon: LineChart }
];

export function DashboardLayout() {
  const auth = useAuth();
  if (!auth.isAuthenticated) return <Navigate to="/signin" replace />;
  const visibleNav = auth.isPlatformStaff
    ? [...nav, { to: "/app/superadmin", label: "Superadmin", icon: ShieldCheck }]
    : nav;

  return (
    <div className="min-h-screen bg-panel text-ink">
      <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-line bg-white p-4 md:block">
        <div className="mb-6 flex items-center gap-3">
          <div className="grid h-10 w-10 place-items-center rounded-md bg-teal text-white">
            <Bot size={21} />
          </div>
          <div>
            <p className="text-sm font-semibold">Ethical Dialogue AI</p>
            <p className="text-xs text-slate-500">{auth.workspace?.name ?? "Workspace"}</p>
          </div>
        </div>
        <nav className="space-y-1">
          {visibleNav.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/app"}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-md px-3 py-2 text-sm ${isActive ? "bg-teal text-white" : "text-slate-700 hover:bg-panel"}`
              }
            >
              <item.icon size={17} />
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <div className="md:pl-64">
        <header className="sticky top-0 z-10 flex h-16 items-center justify-between border-b border-line bg-white px-4 md:px-8">
          <div>
            <p className="text-sm font-medium">{auth.workspace?.business_name ?? "Demo workspace"}</p>
            <p className="text-xs text-slate-500">{auth.me?.user.email}</p>
          </div>
          <Button variant="secondary" onClick={auth.signOut}>Sign out</Button>
        </header>
        <main className="mx-auto max-w-7xl p-4 md:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

import { FormEvent, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { createBrowserRouter, Navigate, Route, Routes, useNavigate } from "react-router-dom";
import { AlertTriangle, CheckCircle2, Eye, EyeOff, KeyRound, LogOut, Search, ShieldCheck, Sparkles, X, XCircle } from "lucide-react";

import { api, tokenStore } from "./services/api";
import type { PlatformOverview } from "./types/api";

const metricLabels: Array<{ key: keyof PlatformOverview; label: string }> = [
  { key: "users", label: "Foydalanuvchilar" },
  { key: "active_workspaces", label: "Faol ish joylari" },
  { key: "opportunities", label: "Imkoniyatlar" },
  { key: "consent_grants", label: "Roziliklar" },
  { key: "leads", label: "Lidlar" },
  { key: "telegram_connections", label: "Telegram ulanishlari" }
];

function StatusMark({ ok }: { ok: boolean }) {
  return (
    <span className={`inline-flex items-center gap-1 text-sm font-medium ${ok ? "text-emerald" : "text-danger"}`}>
      {ok ? <CheckCircle2 size={16} /> : <XCircle size={16} />}
      {ok ? "Sozlangan" : "Yetishmayapti"}
    </span>
  );
}

function AccessDenied() {
  return (
    <main className="grid min-h-screen place-items-center bg-surface p-5">
      <section className="max-w-md rounded-md border border-line bg-panel p-6 shadow-sm">
        <div className="mb-4 flex items-center gap-3 text-danger">
          <AlertTriangle size={24} />
          <h1 className="text-2xl font-semibold">Ruxsat yo'q</h1>
        </div>
        <p className="text-muted">Bu panel faqat platforma xodimlari uchun.</p>
      </section>
    </main>
  );
}

function SignInPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      const result = await api.login(email, password);
      tokenStore.set(result.access, result.refresh);
      navigate("/app");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Kirish amalga oshmadi");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="grid min-h-screen place-items-center bg-ink px-5 py-10 text-white">
      <section className="w-full max-w-md rounded-md border border-white/10 bg-white p-6 text-ink shadow-2xl">
        <div className="mb-6 flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-md bg-emerald text-white">
            <ShieldCheck size={22} />
          </div>
          <div>
            <h1 className="text-xl font-semibold">Superadmin</h1>
            <p className="text-sm text-muted">Platforma boshqaruvi</p>
          </div>
        </div>
        <form onSubmit={submit} className="space-y-4">
          <label className="block text-sm font-medium">
            Email
            <input className="mt-1 w-full rounded-md border border-line px-3 py-2 outline-emerald" value={email} onChange={(event) => setEmail(event.target.value)} />
          </label>
          <label className="block text-sm font-medium">
            Parol
            <div className="relative mt-1">
              <input
                className="w-full rounded-md border border-line px-3 py-2 pr-10 outline-emerald"
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(event) => setPassword(event.target.value)}
              />
              <button
                type="button"
                onClick={() => setShowPassword((v) => !v)}
                aria-label={showPassword ? "Parolni yashirish" : "Parolni ko'rsatish"}
                className="absolute inset-y-0 right-0 grid w-10 place-items-center rounded-md text-muted hover:text-ink"
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </label>
          {error && <p className="rounded-md bg-red-50 p-3 text-sm text-danger">{error}</p>}
          <button className="w-full rounded-md bg-emerald px-4 py-2 font-semibold text-white" disabled={loading}>
            {loading ? "Kirilmoqda" : "Kirish"}
          </button>
        </form>
      </section>
    </main>
  );
}

function PwField({ label, value, onChange }: { label: string; value: string; onChange: (v: string) => void }) {
  const [show, setShow] = useState(false);
  return (
    <label className="block text-sm font-medium">
      {label}
      <div className="relative mt-1">
        <input
          className="w-full rounded-md border border-line px-3 py-2 pr-10 outline-emerald"
          type={show ? "text" : "password"}
          value={value}
          onChange={(event) => onChange(event.target.value)}
        />
        <button
          type="button"
          onClick={() => setShow((v) => !v)}
          aria-label={show ? "Parolni yashirish" : "Parolni ko'rsatish"}
          className="absolute inset-y-0 right-0 grid w-10 place-items-center rounded-md text-muted hover:text-ink"
        >
          {show ? <EyeOff size={18} /> : <Eye size={18} />}
        </button>
      </div>
    </label>
  );
}

function ChangePasswordDialog({ onClose }: { onClose: () => void }) {
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");
  const [done, setDone] = useState(false);
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    if (newPassword !== confirm) {
      setError("Yangi parollar mos kelmadi.");
      return;
    }
    setLoading(true);
    try {
      await api.changePassword(oldPassword, newPassword);
      setDone(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Parolni o'zgartirib bo'lmadi.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-black/40 p-4 text-ink" onClick={onClose}>
      <div className="w-full max-w-sm rounded-lg bg-white p-6 shadow-xl" onClick={(e) => e.stopPropagation()}>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Parolni o'zgartirish</h2>
          <button type="button" onClick={onClose} aria-label="Yopish" className="text-muted hover:text-ink">
            <X size={20} />
          </button>
        </div>
        {done ? (
          <div className="space-y-4">
            <p className="rounded-md bg-emerald-50 p-3 text-sm text-emerald">Parol muvaffaqiyatli yangilandi.</p>
            <button className="w-full rounded-md bg-emerald px-4 py-2 font-semibold text-white" onClick={onClose}>Yopish</button>
          </div>
        ) : (
          <form onSubmit={submit} className="space-y-4">
            <PwField label="Joriy parol" value={oldPassword} onChange={setOldPassword} />
            <PwField label="Yangi parol" value={newPassword} onChange={setNewPassword} />
            <PwField label="Yangi parolni tasdiqlang" value={confirm} onChange={setConfirm} />
            {error && <p className="rounded-md bg-red-50 p-3 text-sm text-danger">{error}</p>}
            <button className="w-full rounded-md bg-emerald px-4 py-2 font-semibold text-white" disabled={loading}>
              {loading ? "Saqlanmoqda" : "Saqlash"}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}

function DashboardPage() {
  const navigate = useNavigate();
  const [showChangePassword, setShowChangePassword] = useState(false);
  const [workspaceSearch, setWorkspaceSearch] = useState("");
  const [userSearch, setUserSearch] = useState("");
  const me = useQuery({ queryKey: ["me"], queryFn: api.me, enabled: Boolean(tokenStore.access) });
  const isStaff = Boolean(me.data?.user.is_staff || me.data?.user.is_superuser);
  const enabled = Boolean(tokenStore.access && isStaff);
  const overview = useQuery({ queryKey: ["overview"], queryFn: api.overview, enabled });
  const integrations = useQuery({ queryKey: ["integrations"], queryFn: api.integrations, enabled });
  const workspaces = useQuery({ queryKey: ["workspaces", workspaceSearch], queryFn: () => api.workspaces(workspaceSearch), enabled });
  const users = useQuery({ queryKey: ["users", userSearch], queryFn: () => api.users(userSearch), enabled });
  const events = useQuery({ queryKey: ["events"], queryFn: api.events, enabled });

  if (!tokenStore.access) return <Navigate to="/signin" replace />;
  if (me.isLoading) return <main className="min-h-screen bg-surface p-6 text-ink">Yuklanmoqda</main>;
  if (me.isError) return <Navigate to="/signin" replace />;
  if (!isStaff) return <AccessDenied />;

  function signOut() {
    tokenStore.clear();
    navigate("/signin");
  }

  return (
    <main className="min-h-screen bg-surface text-ink">
      <header className="border-b border-line bg-ink text-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4">
          <div className="flex items-center gap-3">
            <div className="grid h-10 w-10 place-items-center rounded-md bg-gold text-ink">
              <Sparkles size={20} />
            </div>
            <div>
              <p className="font-semibold">Superadmin</p>
              <p className="text-sm text-white/70">{me.data?.user.email}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button className="inline-flex items-center gap-2 rounded-md border border-white/20 px-3 py-2 text-sm" onClick={() => setShowChangePassword(true)}>
              <KeyRound size={16} /> Parol
            </button>
            <button className="inline-flex items-center gap-2 rounded-md border border-white/20 px-3 py-2 text-sm" onClick={signOut}>
              <LogOut size={16} /> Chiqish
            </button>
          </div>
        </div>
      </header>
      {showChangePassword && <ChangePasswordDialog onClose={() => setShowChangePassword(false)} />}

      <div className="mx-auto max-w-7xl space-y-6 px-5 py-6">
        <div>
          <p className="text-sm font-semibold uppercase text-emerald">Platforma nazorati</p>
          <h1 className="text-3xl font-semibold">Platforma boshqaruvi</h1>
        </div>

        <section className="grid gap-3 md:grid-cols-3 xl:grid-cols-6">
          {overview.data && metricLabels.map((metric) => (
            <article key={metric.key} className="rounded-md border border-line bg-panel p-4 shadow-sm">
              <p className="text-xs font-semibold uppercase text-muted">{metric.label}</p>
              <p className="mt-2 text-3xl font-semibold">{overview.data[metric.key]}</p>
            </article>
          ))}
        </section>

        <section className="grid gap-4 lg:grid-cols-2">
          <article className="rounded-md border border-line bg-panel p-5 shadow-sm">
            <h2 className="mb-4 font-semibold">AI integratsiyasi</h2>
            {integrations.data && (
              <dl className="grid gap-3 text-sm">
                <div className="flex justify-between"><dt className="text-muted">Provayder</dt><dd>{integrations.data.ai.provider}</dd></div>
                <div className="flex justify-between"><dt className="text-muted">Model</dt><dd>{integrations.data.ai.model}</dd></div>
                <div className="flex justify-between"><dt className="text-muted">Kalit</dt><dd><StatusMark ok={integrations.data.ai.credential_configured} /></dd></div>
                <div className="flex justify-between"><dt className="text-muted">Vertex loyiha</dt><dd><StatusMark ok={integrations.data.ai.vertex_project_configured} /></dd></div>
              </dl>
            )}
          </article>
          <article className="rounded-md border border-line bg-panel p-5 shadow-sm">
            <h2 className="mb-4 font-semibold">Telegram integratsiyasi</h2>
            {integrations.data && (
              <dl className="grid gap-3 text-sm">
                <div className="flex justify-between"><dt className="text-muted">Provayder</dt><dd>{integrations.data.telegram.provider}</dd></div>
                <div className="flex justify-between"><dt className="text-muted">Bot token</dt><dd><StatusMark ok={integrations.data.telegram.bot_token_configured} /></dd></div>
                <div className="flex justify-between"><dt className="text-muted">Webhook sir</dt><dd><StatusMark ok={integrations.data.telegram.webhook_secret_configured} /></dd></div>
                <div className="flex justify-between"><dt className="text-muted">Webhook URL</dt><dd><StatusMark ok={integrations.data.telegram.webhook_base_url_configured} /></dd></div>
              </dl>
            )}
          </article>
        </section>

        <section className="grid gap-4 xl:grid-cols-2">
          <article className="rounded-md border border-line bg-panel p-5 shadow-sm">
            <div className="mb-4 flex items-center justify-between gap-3">
              <h2 className="font-semibold">Ish joylari</h2>
              <label className="flex items-center gap-2 rounded-md border border-line px-3 py-2 text-sm">
                <Search size={16} />
                <input className="w-44 outline-none" value={workspaceSearch} onChange={(event) => setWorkspaceSearch(event.target.value)} placeholder="Qidirish" />
              </label>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="text-xs uppercase text-muted"><tr><th className="py-2">Nomi</th><th>Egasi</th><th>Tarif</th><th>Lidlar</th></tr></thead>
                <tbody className="divide-y divide-line">
                  {workspaces.data?.results.map((workspace) => (
                    <tr key={workspace.id}><td className="py-3 font-medium">{workspace.name}</td><td>{workspace.owner ?? "Egasi yo'q"}</td><td>{workspace.plan ?? "Tarifsiz"}</td><td>{workspace.lead_count}</td></tr>
                  ))}
                </tbody>
              </table>
            </div>
          </article>
          <article className="rounded-md border border-line bg-panel p-5 shadow-sm">
            <div className="mb-4 flex items-center justify-between gap-3">
              <h2 className="font-semibold">Foydalanuvchilar</h2>
              <label className="flex items-center gap-2 rounded-md border border-line px-3 py-2 text-sm">
                <Search size={16} />
                <input className="w-44 outline-none" value={userSearch} onChange={(event) => setUserSearch(event.target.value)} placeholder="Qidirish" />
              </label>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="text-xs uppercase text-muted"><tr><th className="py-2">Email</th><th>Ism</th><th>A'zolik</th><th>Rol</th></tr></thead>
                <tbody className="divide-y divide-line">
                  {users.data?.results.map((user) => (
                    <tr key={user.id}><td className="py-3">{user.email}</td><td>{user.full_name || "Kiritilmagan"}</td><td>{user.membership_count}</td><td>{user.is_superuser ? "Superuser" : user.is_staff ? "Xodim" : "A'zo"}</td></tr>
                  ))}
                </tbody>
              </table>
            </div>
          </article>
        </section>

        <article className="rounded-md border border-line bg-panel p-5 shadow-sm">
          <h2 className="mb-4 font-semibold">So'nggi hodisalar</h2>
          <div className="divide-y divide-line">
            {events.data?.results.map((event) => (
              <div key={event.id} className="py-3">
                <p className="font-medium">{event.summary}</p>
                <p className="text-sm text-muted">{event.workspace} - {event.source}</p>
              </div>
            ))}
          </div>
        </article>
      </div>
    </main>
  );
}

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to={tokenStore.access ? "/app" : "/signin"} replace />} />
      <Route path="/signin" element={<SignInPage />} />
      <Route path="/app" element={<DashboardPage />} />
    </Routes>
  );
}

export const router = createBrowserRouter([
  { path: "*", element: <AppRoutes /> }
]);

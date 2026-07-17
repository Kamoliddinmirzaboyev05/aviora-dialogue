import { FormEvent, useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { Bot, Eye, EyeOff } from "lucide-react";

import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { useAuth } from "./AuthProvider";

export function SignInPage() {
  const auth = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  if (auth.isAuthenticated && auth.workspace) return <Navigate to="/app" replace />;

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      await auth.signIn(email, password);
      navigate("/app");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Kirishda xatolik");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="grid min-h-screen place-items-center bg-panel px-4">
      <Card className="w-full max-w-md">
        <div className="mb-6 flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-md bg-teal text-white">
            <Bot size={22} />
          </div>
          <div>
            <h1 className="text-xl font-semibold">Aviora Dialogue</h1>
            <p className="text-sm text-slate-600">Ish maydoni boshqaruv paneli</p>
          </div>
        </div>
        <form onSubmit={submit} className="space-y-4">
          <label className="block text-sm font-medium">
            Email
            <input className="focus-ring mt-1 w-full rounded-md border border-line px-3 py-2" value={email} onChange={(event) => setEmail(event.target.value)} />
          </label>
          <label className="block text-sm font-medium">
            Parol
            <div className="relative mt-1">
              <input
                className="focus-ring w-full rounded-md border border-line px-3 py-2 pr-10"
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(event) => setPassword(event.target.value)}
              />
              <button
                type="button"
                onClick={() => setShowPassword((v) => !v)}
                aria-label={showPassword ? "Parolni yashirish" : "Parolni ko'rsatish"}
                className="focus-ring absolute inset-y-0 right-0 grid w-10 place-items-center rounded-md text-slate-500 hover:text-slate-800"
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </label>
          {error && <p className="rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</p>}
          <Button className="w-full" disabled={loading}>{loading ? "Kirilmoqda" : "Kirish"}</Button>
        </form>
      </Card>
    </main>
  );
}

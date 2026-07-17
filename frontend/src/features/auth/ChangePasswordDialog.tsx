import { FormEvent, useState } from "react";
import { Eye, EyeOff, X } from "lucide-react";

import { Button } from "../../components/ui/Button";
import { api } from "../../services/api";

function PasswordField({
  label,
  value,
  onChange
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
}) {
  const [show, setShow] = useState(false);
  return (
    <label className="block text-sm font-medium">
      {label}
      <div className="relative mt-1">
        <input
          className="focus-ring w-full rounded-md border border-line px-3 py-2 pr-10"
          type={show ? "text" : "password"}
          value={value}
          onChange={(event) => onChange(event.target.value)}
        />
        <button
          type="button"
          onClick={() => setShow((v) => !v)}
          aria-label={show ? "Parolni yashirish" : "Parolni ko'rsatish"}
          className="focus-ring absolute inset-y-0 right-0 grid w-10 place-items-center rounded-md text-slate-500 hover:text-slate-800"
        >
          {show ? <EyeOff size={18} /> : <Eye size={18} />}
        </button>
      </div>
    </label>
  );
}

export function ChangePasswordDialog({ onClose }: { onClose: () => void }) {
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
    <div className="fixed inset-0 z-50 grid place-items-center bg-black/40 p-4" onClick={onClose}>
      <div className="w-full max-w-sm rounded-lg bg-white p-6 shadow-xl" onClick={(e) => e.stopPropagation()}>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Parolni o'zgartirish</h2>
          <button type="button" onClick={onClose} aria-label="Yopish" className="text-slate-400 hover:text-slate-700">
            <X size={20} />
          </button>
        </div>
        {done ? (
          <div className="space-y-4">
            <p className="rounded-md bg-emerald-50 p-3 text-sm text-emerald-700">Parol muvaffaqiyatli yangilandi.</p>
            <Button className="w-full" onClick={onClose}>Yopish</Button>
          </div>
        ) : (
          <form onSubmit={submit} className="space-y-4">
            <PasswordField label="Joriy parol" value={oldPassword} onChange={setOldPassword} />
            <PasswordField label="Yangi parol" value={newPassword} onChange={setNewPassword} />
            <PasswordField label="Yangi parolni tasdiqlang" value={confirm} onChange={setConfirm} />
            {error && <p className="rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</p>}
            <Button className="w-full" disabled={loading}>{loading ? "Saqlanmoqda" : "Saqlash"}</Button>
          </form>
        )}
      </div>
    </div>
  );
}

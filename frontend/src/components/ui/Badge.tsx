export function Badge({ children, tone = "neutral" }: { children: string | number; tone?: "neutral" | "green" | "amber" | "red" }) {
  const classes = {
    neutral: "bg-slate-100 text-slate-700",
    green: "bg-emerald-50 text-emerald-700",
    amber: "bg-amber-50 text-amber-700",
    red: "bg-red-50 text-red-700"
  };
  return <span className={`inline-flex rounded-full px-2 py-1 text-xs font-medium ${classes[tone]}`}>{children}</span>;
}

import { ArrowRight, CheckCircle2, MessageSquareText, ShieldCheck, Sparkles, UserCheck } from "lucide-react";

import heroImage from "./assets/ethical-dialogue-hero.png";

const adminUrl = import.meta.env.VITE_ADMIN_URL ?? "/signin";

const workflow = [
  {
    title: "Telegram conversations",
    text: "Monitor product questions and buyer intent without turning private chats into a black box.",
    icon: MessageSquareText
  },
  {
    title: "Consent requested",
    text: "Ask permission before product recommendations move into a guided sales flow.",
    icon: ShieldCheck
  },
  {
    title: "Human approval",
    text: "Review drafts, safety flags, and context before responses reach the customer.",
    icon: UserCheck
  },
  {
    title: "Qualified leads",
    text: "Convert approved conversations into clear opportunities for the sales team.",
    icon: Sparkles
  }
];

export function App() {
  return (
    <main className="min-h-screen bg-cloud text-ink">
      <section className="relative overflow-hidden bg-ink text-white">
        <img className="absolute inset-0 h-full w-full object-cover opacity-35" src={heroImage} alt="" />
        <div className="relative mx-auto grid min-h-[86vh] max-w-7xl content-center gap-10 px-5 py-16 md:grid-cols-[1.05fr_0.95fr] md:px-8">
          <div className="max-w-3xl">
            <p className="mb-4 text-sm font-semibold uppercase tracking-[0.18em] text-gold">Consent-first automation</p>
            <h1 className="text-4xl font-semibold leading-tight md:text-6xl">Ethical Dialogue AI</h1>
            <p className="mt-5 max-w-2xl text-lg leading-8 text-slate-100">
              Turn Telegram product conversations into approved responses and qualified leads while keeping consent, safety, and human review at the center.
            </p>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <a className="inline-flex items-center justify-center gap-2 rounded-md bg-gold px-5 py-3 font-semibold text-ink" href={adminUrl}>
                Sign in <ArrowRight size={18} />
              </a>
              <a className="inline-flex items-center justify-center rounded-md border border-white/35 px-5 py-3 font-semibold text-white" href="#workflow">
                See workflow
              </a>
            </div>
          </div>
          <div className="self-end rounded-md border border-white/20 bg-white/10 p-5 backdrop-blur">
            <p className="text-sm font-medium text-gold">Operator snapshot</p>
            <div className="mt-4 grid gap-3">
              {["12 conversations analyzed", "7 drafts awaiting approval", "4 consent grants captured"].map((item) => (
                <div key={item} className="flex items-center gap-3 rounded-md bg-white/10 px-4 py-3">
                  <CheckCircle2 size={18} className="text-gold" />
                  <span>{item}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section id="workflow" className="mx-auto max-w-7xl px-5 py-16 md:px-8">
        <div className="max-w-2xl">
          <p className="text-sm font-semibold uppercase text-coral">Workflow</p>
          <h2 className="mt-2 text-3xl font-semibold">From conversation to qualified lead</h2>
        </div>
        <div className="mt-8 grid gap-4 md:grid-cols-4">
          {workflow.map((item) => (
            <article key={item.title} className="rounded-md border border-line bg-white p-5">
              <item.icon className="text-moss" size={24} />
              <h3 className="mt-4 font-semibold">{item.title}</h3>
              <p className="mt-2 text-sm leading-6 text-slate-600">{item.text}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="border-y border-line bg-white">
        <div className="mx-auto grid max-w-7xl gap-8 px-5 py-16 md:grid-cols-3 md:px-8">
          <div>
            <p className="text-sm font-semibold uppercase text-coral">Trust</p>
            <h2 className="mt-2 text-3xl font-semibold">Built for careful teams</h2>
          </div>
          <div className="grid gap-4 sm:grid-cols-3 md:col-span-2">
            {["Consent records", "Audit history", "No secret exposure"].map((item) => (
              <div key={item} className="rounded-md bg-cloud p-5 font-medium">{item}</div>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-5 py-16 md:px-8">
        <div className="rounded-md bg-moss px-6 py-10 text-white md:px-10">
          <h2 className="text-3xl font-semibold">Run the workflow from one focused dashboard.</h2>
          <p className="mt-3 max-w-2xl text-white/80">
            Review approvals, monitor integrations, convert leads, and keep every AI-assisted conversation accountable.
          </p>
          <a className="mt-6 inline-flex items-center gap-2 rounded-md bg-white px-5 py-3 font-semibold text-moss" href={adminUrl}>
            Sign in <ArrowRight size={18} />
          </a>
        </div>
      </section>
    </main>
  );
}

import { useEffect, useState, type CSSProperties } from "react";
import {
  ArrowUpRight,
  Check,
  CheckCheck,
  Globe,
  Phone,
  Plus,
  Radar,
  Send,
  ShieldCheck,
  Sparkles,
  UserCheck,
  Zap
} from "lucide-react";

const adminUrl = import.meta.env.VITE_ADMIN_URL ?? "/signin";

const delay = (ms: number): CSSProperties => ({ ["--reveal-delay" as string]: `${ms}ms` } as CSSProperties);

const navLinks = [
  { label: "Biz haqimizda", href: "#biz-haqimizda" },
  { label: "Qanday ishlaydi", href: "#qanday-ishlaydi" },
  { label: "Afzalliklar", href: "#afzalliklar" },
  { label: "Savollar", href: "#savollar" }
];

const stats = [
  { value: "24/7", label: "to'xtovsiz kuzatuv" },
  { value: "0", label: "spam xabar" },
  { value: "3 daqiqa", label: "ulash va sozlash" },
  { value: "100%", label: "rozilik bilan" }
];

const steps = [
  {
    icon: Radar,
    title: "Kuzatadi",
    text: "Botni Telegram guruhlaringizga ulaysiz — u tegishli suhbatlarni real vaqtda, tinch kuzatib boradi."
  },
  {
    icon: Sparkles,
    title: "Aniqlaydi",
    text: "Mahsulotingiz yechadigan muammoni aytgan foydalanuvchilarni topadi va niyatini baholaydi."
  },
  {
    icon: ShieldCheck,
    title: "Rozilik so'raydi",
    text: "Javob berishdan avval o'zini tanishtiradi va ruxsat so'raydi — hech kim bezovta bo'lmaydi."
  },
  {
    icon: UserCheck,
    title: "Lid yetkazadi",
    text: "Rozilik olgach, tayyor va issiq lidni to'g'ridan-to'g'ri menejeringizga uzatadi."
  }
];

const features = [
  {
    title: "G'ashiga tegish emas, balki lidlarni jalb qilish",
    text: "Yopishqoq reklama o'rniga siz sodiq mijozlarga ega bo'lasiz. Bot suhbatga faqat sizning yordamingiz haqiqatan ham kerak bo'lganda qo'shiladi, bu esa brendga ishonchni shakllantiradi."
  },
  {
    title: "To'liq avtomatlashtirish",
    text: "Yordamchi 24/7 ishlaydi va bir vaqtning o'zida o'nlab chatlardagi tegishli muhokamalarni kuzatib boradi. Siz menejerlar vaqtini monitoringga sarflamasdan, tayyor (issiq) lidlar olasiz."
  },
  {
    title: "Axloqiylik va shaffoflik",
    text: "Bizning «avval so'ra» yondashuvimiz salbiy munosabatni istisno qiladi. Bot har doim o'zini tanishtiradi va faqat chat ma'murlarining ruxsati bilan ishlaydi, bu uning faoliyatining qonuniyligini ta'minlaydi."
  },
  {
    title: "Brend tanilishini oshirish",
    text: "O'z auditoriyangiz uchun muhim bo'lgan hamjamiyatlarda ekspert-yordamchi sifatida ishtirok etib, siz nafaqat mijozlar topasiz, balki brendingizning foydali va g'amxo'r sifatidagi obro'sini ham mustahkamlaysiz."
  }
];

const faqs = [
  {
    q: "Aviora Dialogue nima?",
    a: "Bu Telegram hamjamiyatlarida ishlaydigan intellektual yordamchi: ochiq suhbatlardan mahsulotingizga qiziqqan mijozlarni topadi va ularning roziligi bilan yechim taklif qiladi."
  },
  {
    q: "U potensial mijozlarni qanday topadi?",
    a: "Guruh va kanallardagi muhokamalarni tahlil qilib, sizning mahsulotingiz yechadigan muammoni aytgan foydalanuvchilarni aniqlaydi."
  },
  {
    q: "Bot mening foydalanuvchilarimning g'ashiga tegmaydimi?",
    a: "Yo'q. U spam yubormaydi — faqat mavzu bevosita mos kelganda va chat ma'muri ruxsat bergan joyda javob beradi."
  },
  {
    q: "Bu qanday hamjamiyatlar uchun mos keladi?",
    a: "Mahsulot, xizmat yoki sohaga oid ochiq Telegram guruh va kanallar — auditoriyangiz faol muloqot qiladigan har qanday joy."
  },
  {
    q: "Bot nima va qanday javob berishni qayerdan biladi?",
    a: "Siz bergan mahsulot ma'lumotlari, ohang va qoidalar asosida. U kontekstni tushunib, brendingizga mos javob shakllantiradi."
  },
  {
    q: "Botning javoblarini sozlasa bo'ladimi?",
    a: "Ha, ohang, iboralar va ruxsat etilgan mavzularni to'liq sozlaysiz. Har bir javob yuborilishidan oldin tasdiqdan o'tkazilishi mumkin."
  },
  {
    q: "Chat ma'muridan ruxsat olish kerakmi?",
    a: "Ha. Bot faqat ma'mur roziligi bilan ishlaydi — bu uning faoliyatini shaffof va qonuniy qiladi."
  },
  {
    q: "Agar bot yordam bera olmasa-chi?",
    a: "Murakkab holatda suhbatni menejeringizga uzatadi, shunda inson operator kontekst bilan davom ettiradi."
  },
  {
    q: "Uning samaradorligini qanday o'lchash mumkin?",
    a: "Boshqaruv panelida topilgan lidlar, tasdiqlangan javoblar va konversiya ko'rsatkichlarini real vaqtda kuzatasiz."
  },
  {
    q: "Aviora Dialogue'dan foydalanishni qanday boshlash kerak?",
    a: "«Kirish» tugmasi orqali ro'yxatdan o'ting, botni guruhingizga ulang va mahsulot ma'lumotlarini kiriting — bir necha daqiqada tayyor."
  }
];

function useScrollReveal() {
  useEffect(() => {
    const els = Array.from(document.querySelectorAll<HTMLElement>(".reveal"));
    if (!("IntersectionObserver" in window)) {
      els.forEach((el) => el.classList.add("is-visible"));
      return;
    }
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
    );
    els.forEach((el) => io.observe(el));
    return () => io.disconnect();
  }, []);
}

function Logo() {
  return (
    <span className="flex items-center gap-2.5">
      <svg width="34" height="34" viewBox="0 0 34 34" fill="none" aria-hidden>
        <path d="M14 9c5.5 0 9 3.4 9 8s-4 8-9.5 8C8.5 25 5 22 5 17.5 5 13 8.5 9 14 9Z" fill="#fff" opacity="0.92" />
        <path d="M21 9c5 0 8 3.2 8 7.5S25.5 24 20.5 24 13 20.8 13 16.5 16 9 21 9Z" fill="#b9a7ff" opacity="0.85" />
      </svg>
      <span className="text-[15px] font-bold leading-4 tracking-tight text-white">
        Aviora<br />Dialogue
      </span>
    </span>
  );
}

function Nav() {
  return (
    <header className="sticky top-0 z-30 border-b border-white/5 bg-night/70 backdrop-blur-xl">
      <nav className="mx-auto flex max-w-6xl items-center justify-between px-5 py-4 md:px-8">
        <a href="#" aria-label="Aviora Dialogue"><Logo /></a>
        <div className="hidden items-center gap-8 md:flex">
          {navLinks.map((l) => (
            <a key={l.href} href={l.href} className="text-sm font-medium text-slate-300 transition hover:text-white">
              {l.label}
            </a>
          ))}
        </div>
        <div className="flex items-center gap-3">
          <span className="hidden items-center gap-1.5 rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-xs font-medium text-slate-200 sm:inline-flex">
            <Globe size={14} /> O'zbekcha
          </span>
          <a
            href={adminUrl}
            className="rounded-lg bg-violet px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-violet/30 transition hover:bg-violet/90"
          >
            Kirish
          </a>
        </div>
      </nav>
    </header>
  );
}

function ChatMock() {
  return (
    <div className="reveal relative w-full max-w-sm" style={delay(120)}>
      <div className="pointer-events-none absolute -inset-6 -z-10 animate-float rounded-full bg-gradient-to-br from-glow/40 via-violet/40 to-transparent blur-3xl" />
      <div className="overflow-hidden rounded-3xl border border-white/10 bg-panel/80 shadow-2xl shadow-black/50 backdrop-blur">
        <div className="flex items-center gap-3 border-b border-white/10 bg-white/5 px-5 py-3.5">
          <span className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-glow to-violet text-sm font-bold text-white">A</span>
          <div className="leading-tight">
            <p className="text-sm font-semibold text-white">IT-xizmatlar guruhi</p>
            <p className="flex items-center gap-1 text-xs text-emerald-400">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" /> Aviora yordamchi faol
            </p>
          </div>
        </div>
        <div className="space-y-3 p-5">
          <div className="max-w-[80%] rounded-2xl rounded-tl-sm bg-white/10 px-4 py-2.5 text-sm text-slate-100">
            Kimda yaxshi CRM bor? Excel'dan charchadim 😩
          </div>
          <div className="ml-auto max-w-[86%] rounded-2xl rounded-tr-sm bg-gradient-to-br from-violet to-glow px-4 py-2.5 text-sm text-white">
            <span className="mb-1 block text-[11px] font-semibold uppercase tracking-wide text-white/70">Aviora yordamchi</span>
            Ruxsatingiz bilan mos yechimni tavsiya qilsam bo'ladimi?
            <span className="mt-1 flex items-center justify-end gap-1 text-[10px] text-white/70">10:24 <CheckCheck size={12} /></span>
          </div>
          <div className="max-w-[70%] rounded-2xl rounded-tl-sm bg-white/10 px-4 py-2.5 text-sm text-slate-100">Ha, mayli 👍</div>
          <div className="flex flex-wrap gap-2 pt-1">
            <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-400/30 bg-emerald-400/10 px-3 py-1 text-xs font-medium text-emerald-300">
              <Check size={13} /> Rozilik olindi
            </span>
            <span className="inline-flex items-center gap-1.5 rounded-full border border-violet/30 bg-violet/10 px-3 py-1 text-xs font-medium text-violet">
              <Sparkles size={13} /> Yangi lid yaratildi
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

function Hero() {
  return (
    <section id="biz-haqimizda" className="relative overflow-hidden">
      <div className="dotgrid pointer-events-none absolute inset-0" />
      <div className="pointer-events-none absolute -top-40 left-1/2 h-[520px] w-[720px] -translate-x-1/2 rounded-full bg-violet/20 blur-[140px]" />
      <div className="relative mx-auto grid max-w-6xl items-center gap-12 px-5 py-20 md:grid-cols-[1.05fr_0.95fr] md:px-8 md:py-28">
        <div className="reveal">
          <span className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3.5 py-1.5 text-xs font-medium text-slate-200">
            <span className="h-1.5 w-1.5 rounded-full bg-glow" /> Telegram uchun rozilikka asoslangan sotuv yordamchisi
          </span>
          <h1 className="mt-6 text-5xl font-extrabold leading-[1.05] tracking-tight text-white md:text-6xl">
            Aviora Dialogue
          </h1>
          <p className="mt-5 max-w-xl text-lg leading-8 text-slate-300">
            Chatlarda axloqiy marketing uchun intellektual yordamchi. Mijozlar muammo haqida gapirganda
            ularni topadi va ularning roziligi bilan yechim taklif qiladi.
          </p>
          <div className="mt-8 flex flex-col gap-3 sm:flex-row">
            <a
              href={adminUrl}
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-violet px-6 py-3.5 font-semibold text-white shadow-lg shadow-violet/30 transition hover:bg-violet/90"
            >
              Bepul boshlash <ArrowUpRight size={18} />
            </a>
            <a
              href="#qanday-ishlaydi"
              className="inline-flex items-center justify-center rounded-xl border border-white/15 px-6 py-3.5 font-semibold text-white transition hover:bg-white/5"
            >
              Qanday ishlaydi
            </a>
          </div>
        </div>
        <div className="flex justify-center md:justify-end">
          <ChatMock />
        </div>
      </div>

      <div className="relative mx-auto grid max-w-6xl gap-px overflow-hidden rounded-2xl border border-stroke bg-stroke sm:grid-cols-2 md:mx-8 md:grid-cols-4 lg:mx-auto">
        {stats.map((s, i) => (
          <div key={s.label} className="reveal bg-deep px-6 py-7 text-center" style={delay(i * 70)}>
            <p className="bg-gradient-to-r from-white to-slate-300 bg-clip-text text-3xl font-extrabold tracking-tight text-transparent">
              {s.value}
            </p>
            <p className="mt-1 text-sm text-slate-400">{s.label}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

function Steps() {
  return (
    <section id="qanday-ishlaydi" className="mx-auto max-w-6xl px-5 py-16 md:px-8 md:py-24">
      <div className="reveal max-w-2xl">
        <span className="text-sm font-semibold uppercase tracking-wider text-violet">Qanday ishlaydi</span>
        <h2 className="mt-3 text-4xl font-extrabold leading-tight tracking-tight text-white md:text-5xl">
          Suhbatdan issiq lidgacha — to'rt qadam
        </h2>
      </div>
      <div className="mt-12 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {steps.map((step, i) => (
          <article
            key={step.title}
            className="reveal group relative rounded-2xl border border-stroke bg-panel/50 p-6 transition hover:border-violet/40 hover:bg-panel"
            style={delay(i * 90)}
          >
            <span className="absolute right-5 top-5 text-2xl font-black text-white/10 transition group-hover:text-violet/30">
              0{i + 1}
            </span>
            <span className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-violet/20 to-glow/10 text-violet">
              <step.icon size={22} />
            </span>
            <h3 className="mt-5 text-lg font-bold text-white">{step.title}</h3>
            <p className="mt-2 text-sm leading-6 text-slate-400">{step.text}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

function Features() {
  return (
    <section id="afzalliklar" className="mx-auto max-w-6xl px-5 py-16 md:px-8 md:py-24">
      <h2 className="reveal max-w-md text-4xl font-extrabold leading-tight tracking-tight text-white md:text-5xl">
        Aviora Dialogue afzalliklari
      </h2>
      <div className="mt-12 grid gap-5 md:grid-cols-2">
        {features.map((f, i) => (
          <article
            key={f.title}
            className="reveal group relative flex min-h-[280px] flex-col justify-between overflow-hidden rounded-2xl border border-stroke bg-panel/60 p-7 transition hover:border-violet/50 hover:bg-panel"
            style={delay((i % 2) * 90)}
          >
            <div className="pointer-events-none absolute -right-16 -top-16 h-40 w-40 rounded-full bg-violet/10 opacity-0 blur-2xl transition group-hover:opacity-100" />
            <span className="relative flex h-11 w-11 items-center justify-center self-end rounded-full border border-white/10 bg-white/5 text-slate-200 transition group-hover:bg-violet group-hover:text-white">
              <ArrowUpRight size={18} />
            </span>
            <div className="relative">
              <p className="text-[15px] leading-7 text-slate-400">{f.text}</p>
              <h3 className="mt-6 text-xl font-bold text-white">{f.title}</h3>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

function Faq() {
  const [open, setOpen] = useState<number | null>(0);
  return (
    <section id="savollar" className="mx-auto max-w-6xl px-5 py-16 md:px-8 md:py-24">
      <div className="reveal rounded-3xl border border-stroke bg-panel/40 p-6 md:grid md:grid-cols-[0.8fr_1.2fr] md:gap-10 md:p-12">
        <h2 className="text-4xl font-extrabold leading-tight tracking-tight text-white md:text-5xl">
          Tez-tez beriladigan{" "}
          <span className="bg-gradient-to-r from-violet to-glow bg-clip-text text-transparent">Savollar</span>
        </h2>
        <div className="mt-8 divide-y divide-white/5 md:mt-0">
          {faqs.map((item, i) => {
            const active = open === i;
            return (
              <div key={item.q}>
                <button
                  type="button"
                  onClick={() => setOpen(active ? null : i)}
                  aria-expanded={active}
                  className="flex w-full items-center justify-between gap-4 py-4 text-left"
                >
                  <span className={`text-[15px] font-medium transition ${active ? "text-white" : "text-slate-300"}`}>
                    {item.q}
                  </span>
                  <Plus
                    size={18}
                    className={`shrink-0 text-violet transition-transform duration-300 ${active ? "rotate-45" : ""}`}
                  />
                </button>
                <div
                  className={`grid overflow-hidden transition-all duration-300 ${active ? "grid-rows-[1fr] pb-4" : "grid-rows-[0fr]"}`}
                >
                  <p className="min-h-0 text-sm leading-7 text-slate-400">{item.a}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

function CtaBand() {
  return (
    <section className="mx-auto max-w-6xl px-5 pb-8 md:px-8">
      <div className="reveal relative overflow-hidden rounded-3xl border border-violet/30 bg-gradient-to-br from-violet/20 via-panel to-deep px-6 py-14 text-center md:px-16">
        <div className="pointer-events-none absolute -left-20 -top-20 h-64 w-64 rounded-full bg-glow/20 blur-3xl" />
        <div className="pointer-events-none absolute -bottom-24 -right-16 h-64 w-64 rounded-full bg-violet/20 blur-3xl" />
        <h2 className="relative mx-auto max-w-2xl text-3xl font-extrabold leading-tight tracking-tight text-white md:text-4xl">
          Bugun birinchi issiq lidingizni oling
        </h2>
        <p className="relative mx-auto mt-4 max-w-xl text-slate-300">
          Botni guruhingizga ulang, mahsulotingizni kiriting — qolganini Aviora Dialogue bajaradi.
        </p>
        <a
          href={adminUrl}
          className="relative mt-8 inline-flex items-center justify-center gap-2 rounded-xl bg-violet px-7 py-4 font-semibold text-white shadow-lg shadow-violet/30 transition hover:bg-violet/90"
        >
          <Zap size={18} /> Bepul boshlash
        </a>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="border-t border-white/5 bg-deep">
      <div className="mx-auto flex max-w-6xl flex-col gap-8 px-5 py-12 md:flex-row md:items-start md:justify-between md:px-8">
        <div className="max-w-xs">
          <Logo />
          <p className="mt-4 text-sm leading-6 text-slate-400">
            Telegram hamjamiyatlari uchun axloqiy va shaffof marketing yordamchisi.
          </p>
        </div>
        <div className="flex flex-col gap-3 text-sm md:items-end">
          <div className="flex flex-wrap gap-x-6 gap-y-2 md:justify-end">
            {navLinks.map((l) => (
              <a key={l.label} href={l.href} className="font-medium text-slate-300 transition hover:text-white">
                {l.label}
              </a>
            ))}
          </div>
          <div className="mt-2 flex flex-wrap gap-3 md:justify-end">
            <a
              href="https://t.me/aviora"
              className="inline-flex items-center gap-2 rounded-lg border border-white/10 bg-white/5 px-4 py-2 font-medium text-slate-200 transition hover:text-white"
            >
              <Send size={15} className="text-violet" /> Aloqa
            </a>
            <a
              href="tel:+998931210023"
              className="inline-flex items-center gap-2 rounded-lg border border-white/10 bg-white/5 px-4 py-2 font-medium text-slate-200 transition hover:text-white"
            >
              <Phone size={15} className="text-violet" /> +998 93 121 00 23
            </a>
          </div>
        </div>
      </div>
      <div className="border-t border-white/5 py-5 text-center text-xs text-slate-500">
        © {new Date().getFullYear()} Aviora Dialogue. Barcha huquqlar himoyalangan.
      </div>
    </footer>
  );
}

export function App() {
  useScrollReveal();
  return (
    <main className="min-h-screen bg-night text-slate-100">
      <Nav />
      <Hero />
      <Steps />
      <Features />
      <Faq />
      <CtaBand />
      <Footer />
    </main>
  );
}

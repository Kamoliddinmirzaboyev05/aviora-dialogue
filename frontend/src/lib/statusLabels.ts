// Backend enum qiymatlarini foydalanuvchiga ko'rinadigan o'zbekcha yorliqlarga o'giradi.
// Qiymatning o'zi (API ga yuboriladigan) o'zgarmaydi — faqat ko'rsatiladigan matn.

export const draftStatusLabels: Record<string, string> = {
  draft: "Qoralama",
  approved: "Tasdiqlangan",
  sent: "Yuborilgan",
  rejected: "Rad etilgan"
};

export const consentStatusLabels: Record<string, string> = {
  not_requested: "So'ralmagan",
  request_sent: "So'rov yuborilgan",
  granted: "Berilgan",
  denied: "Rad etilgan",
  withdrawn: "Qaytarib olingan",
  expired: "Muddati o'tgan"
};

export const opportunityStatusLabels: Record<string, string> = {
  new: "Yangi",
  approved: "Tasdiqlangan",
  rejected: "Rad etilgan",
  permission_requested: "Ruxsat so'ralgan",
  consent_received: "Rozilik olingan",
  converted_to_lead: "Lidga aylantirilgan"
};

export const webhookStatusLabels: Record<string, string> = {
  not_set: "Ulanmagan",
  pending: "Kutilmoqda",
  active: "Faol",
  failed: "Xato"
};

/** Yorliqni topadi; noma'lum qiymat bo'lsa xom qiymatni qaytaradi. */
export function statusLabel(map: Record<string, string>, value: string | null | undefined): string {
  if (!value) return "—";
  return map[value] ?? value;
}

from apps.ai_engine.schemas import ClassificationResult, DraftResult
from apps.products.models import Product


class MockAIProvider:
    def classify_message(self, *, message: str, product: Product, consent_status: str) -> ClassificationResult:
        text = message.lower()
        is_crm_request = "crm" in text and ("recommend" in text or "simple" in text or "sales team" in text)
        return ClassificationResult(
            is_relevant=is_crm_request,
            intent_type="recommendation_request" if is_crm_request else "irrelevant",
            confidence=0.92 if is_crm_request else 0.18,
            detected_problem="Kichik sotuv jamoasi uchun oddiy CRM kerak" if is_crm_request else "",
            urgency="medium" if is_crm_request else "low",
            language="en",
            sentiment="neutral",
            recommended_action="draft_permission_request" if is_crm_request else "ignore",
            concise_reason="Yuboruvchi kichik sotuv jamoasi uchun oddiy CRM tavsiyasini so'rayapti."
            if is_crm_request
            else "Xabar sozlangan mahsulot maqsadiga mos kelmaydi.",
            risk_flags=[],
        )

    def generate_permission_request(self, *, message: str) -> DraftResult:
        return DraftResult(
            text=(
                "Salom, men kichik jamoalarga CRM ish jarayonlarida yordam beradigan biznes uchun AI yordamchiman. "
                "Savolingizni ko'rdim va agar xohlasangiz, mos taklifni ulashishim mumkin. "
                "Qo'shimcha ma'lumot yuborishimni istaysizmi?"
            ),
            concise_reason="Shaffof, avval rozilik so'raydigan javob: AI ekani oshkor qilingan va rozilikdan oldin reklama yo'q.",
        )

    def generate_product_response(self, *, message: str, product: Product, consent_status: str) -> DraftResult:
        return DraftResult(
            text=(
                f"Tasdiqlaganingiz uchun rahmat. {product.name} mos kelishi mumkin, chunki u {product.target_customer.lower()} "
                f"uchun {product.problems_solved.lower()} yordam beradi. Asosiy afzalliklari: {product.benefits.lower()} "
                f"Narxi {product.pricing_model} asosida {product.starting_price} {product.currency} dan boshlanadi. "
                f"Batafsil ma'lumotni shu yerda ko'rishingiz mumkin: {product.website}"
            ),
            concise_reason="Rozilikdan so'ng yoqilgan mahsulot maydonlaridan tuzilgan asoslangan javob.",
        )

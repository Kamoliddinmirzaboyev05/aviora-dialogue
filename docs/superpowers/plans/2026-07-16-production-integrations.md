# Production Integrations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add production-ready Gemini Developer API and Telegram Bot API providers while preserving mock and future Vertex modes.

**Architecture:** Provider factories select strict environment-configured implementations. External clients are injected for tests, normalized at provider boundaries, and exposed through owner/admin-only connection endpoints. Telegram webhooks enter the existing consent-first opportunity service.

**Tech Stack:** Django 5, Django REST Framework, `google-genai`, Pydantic, HTTPX, pytest.

## Global Constraints

- `AI_PROVIDER` supports exactly `mock`, `gemini`, and `vertex`.
- `TELEGRAM_PROVIDER` supports exactly `mock` and `bot_api`.
- Mock mode requires no external secrets.
- Credentials never appear in logs, API responses, database metadata, or exception messages.
- Existing `ClassificationResult` and `DraftResult` remain the internal provider response schema.
- Consent remains mandatory before product information or lead conversion.

---

### Task 1: Gemini Provider And Strict Factory

**Files:**
- Create: `backend/apps/ai_engine/providers/gemini.py`
- Create: `backend/apps/ai_engine/exceptions.py`
- Modify: `backend/apps/ai_engine/services.py`
- Modify: `backend/config/settings.py`
- Modify: `backend/requirements/base.txt`
- Modify: `.env.example`
- Test: `backend/tests/test_ai_providers.py`

**Interfaces:**
- Consumes: `Product`, `ClassificationResult`, `DraftResult`, Django settings.
- Produces: `GeminiAPIProvider(client=None)`, `get_ai_provider()`, `AIProviderConfigurationError`, `AIProviderError`.

- [ ] **Step 1: Write provider selection and normalization tests**

```python
@override_settings(AI_PROVIDER="mock")
def test_mock_provider_needs_no_external_key():
    assert isinstance(get_ai_provider(), MockAIProvider)

@override_settings(AI_PROVIDER="gemini", GEMINI_API_KEY="")
def test_gemini_provider_reports_missing_key():
    with pytest.raises(AIProviderConfigurationError, match="GEMINI_API_KEY"):
        get_ai_provider()

def test_gemini_classification_normalizes_structured_response(product):
    client = FakeGenAIClient(parsed={"is_relevant": True, "intent_type": "recommendation_request", "confidence": 0.91, "detected_problem": "Needs CRM", "urgency": "medium", "language": "en", "sentiment": "neutral", "recommended_action": "draft_permission_request", "concise_reason": "CRM request", "risk_flags": []})
    result = GeminiAPIProvider(api_key="test-key", model="gemini-2.5-flash", client=client).classify_message(message="Recommend a CRM", product=product, consent_status="unknown")
    assert result == ClassificationResult(is_relevant=True, intent_type="recommendation_request", confidence=0.91, detected_problem="Needs CRM", urgency="medium", language="en", sentiment="neutral", recommended_action="draft_permission_request", concise_reason="CRM request", risk_flags=[])
```

- [ ] **Step 2: Run the focused tests and verify RED**

Run: `cd backend && pytest tests/test_ai_providers.py -q`

Expected: collection or import failure because `GeminiAPIProvider` and provider exceptions do not exist.

- [ ] **Step 3: Implement strict settings and provider selection**

```python
AI_PROVIDER = os.getenv("AI_PROVIDER", "mock").strip().lower()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

def get_ai_provider():
    providers = {"mock": MockAIProvider, "gemini": GeminiAPIProvider, "vertex": VertexAIProvider}
    try:
        return providers[settings.AI_PROVIDER]()
    except KeyError as error:
        raise AIProviderConfigurationError(f"Unsupported AI_PROVIDER: {settings.AI_PROVIDER}") from error
```

- [ ] **Step 4: Implement Gemini calls with official structured output**

```python
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

class GeminiClassification(BaseModel):
    is_relevant: bool
    intent_type: str
    confidence: float = Field(ge=0, le=1)
    detected_problem: str
    urgency: str
    language: str
    sentiment: str
    recommended_action: str
    concise_reason: str
    risk_flags: list[str]

response = self.client.models.generate_content(
    model=self.model,
    contents=prompt,
    config=types.GenerateContentConfig(
        temperature=0,
        response_mime_type="application/json",
        response_schema=GeminiClassification,
    ),
)
normalized = GeminiClassification.model_validate(response.parsed)
return ClassificationResult(**normalized.model_dump())
```

- [ ] **Step 5: Add draft normalization and sanitized upstream errors**

```python
try:
    response = self.client.models.generate_content(...)
except Exception as error:
    raise AIProviderError("Gemini request failed. Check provider configuration and service availability.") from error
```

- [ ] **Step 6: Update dependencies and environment template**

```text
google-genai>=2.10,<3
```

```env
AI_PROVIDER=mock
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash
```

- [ ] **Step 7: Run provider tests and commit**

Run: `cd backend && pytest tests/test_ai_providers.py -q`

Expected: all provider tests pass.

```bash
git add backend/apps/ai_engine backend/config/settings.py backend/requirements/base.txt backend/tests/test_ai_providers.py .env.example
git commit -m "feat: add Gemini API provider"
```

### Task 2: Admin-Only AI Connection Test

**Files:**
- Create: `backend/apps/ai_engine/permissions.py`
- Create: `backend/apps/ai_engine/views.py`
- Create: `backend/apps/ai_engine/urls.py`
- Modify: `backend/apps/ai_engine/providers/base.py`
- Modify: `backend/config/urls.py`
- Test: `backend/tests/test_ai_connection_api.py`

**Interfaces:**
- Consumes: `get_ai_provider()`, `WorkspaceMembership`, first active workspace product.
- Produces: `POST /api/v1/ai/test-connection/` with provider, model, state, latency, and normalized classification.

- [ ] **Step 1: Write endpoint authorization and response tests**

```python
def test_workspace_owner_can_test_ai_connection(owner_client, workspace, product, monkeypatch):
    monkeypatch.setattr("apps.ai_engine.views.get_ai_provider", lambda: MockAIProvider())
    response = owner_client.post("/api/v1/ai/test-connection/", {"workspace": str(workspace.id)}, format="json")
    assert response.status_code == 200
    assert response.data["state"] == "connected"
    assert response.data["classification"]["intent_type"] == "recommendation_request"

def test_workspace_reviewer_cannot_test_ai_connection(reviewer_client, workspace):
    response = reviewer_client.post("/api/v1/ai/test-connection/", {"workspace": str(workspace.id)}, format="json")
    assert response.status_code == 403
```

- [ ] **Step 2: Run focused tests and verify RED**

Run: `cd backend && pytest tests/test_ai_connection_api.py -q`

Expected: 404 because the route is not registered.

- [ ] **Step 3: Implement owner/admin permission and fixed-sample endpoint**

```python
membership = WorkspaceMembership.objects.filter(
    workspace_id=request.data.get("workspace"),
    user=request.user,
    is_active=True,
    role__in=[WorkspaceMembership.Role.OWNER, WorkspaceMembership.Role.ADMIN],
).select_related("workspace").first()
if not membership:
    return api_error("workspace_admin_required", "Workspace owner or admin access is required.", status=403)
```

- [ ] **Step 4: Return sanitized provider errors**

```python
except (AIProviderConfigurationError, AIProviderError) as error:
    return api_error("ai_connection_failed", str(error), status=503)
```

- [ ] **Step 5: Run tests and commit**

Run: `cd backend && pytest tests/test_ai_connection_api.py tests/test_ai_providers.py -q`

Expected: all tests pass.

```bash
git add backend/apps/ai_engine backend/config/urls.py backend/tests/test_ai_connection_api.py
git commit -m "feat: add AI connection test endpoint"
```

### Task 3: Official Telegram Bot API Provider And Webhook

**Files:**
- Create: `backend/apps/telegram_integration/providers/bot_api.py`
- Create: `backend/apps/telegram_integration/exceptions.py`
- Modify: `backend/apps/telegram_integration/services.py`
- Modify: `backend/apps/telegram_integration/views.py`
- Modify: `backend/apps/telegram_integration/urls.py`
- Modify: `backend/config/settings.py`
- Modify: `.env.example`
- Test: `backend/tests/test_telegram_provider.py`
- Test: `backend/tests/test_telegram_webhook.py`

**Interfaces:**
- Consumes: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_WEBHOOK_SECRET`, `TELEGRAM_WEBHOOK_BASE_URL`, existing connection/chat/update models and opportunity service.
- Produces: `TelegramBotAPIProvider`, `POST /api/v1/telegram/test-connection/`, `POST /api/v1/telegram/register-webhook/`, and public secret-validated webhook ingestion.

- [ ] **Step 1: Write provider factory and token-safe error tests**

```python
@override_settings(TELEGRAM_PROVIDER="bot_api", TELEGRAM_BOT_TOKEN="")
def test_bot_api_provider_requires_token():
    with pytest.raises(TelegramConfigurationError, match="TELEGRAM_BOT_TOKEN"):
        get_telegram_provider()

def test_bot_api_error_never_contains_token():
    provider = TelegramBotAPIProvider(token="super-secret", client=FailingHTTPClient())
    with pytest.raises(TelegramProviderError) as captured:
        provider.get_me()
    assert "super-secret" not in str(captured.value)
```

- [ ] **Step 2: Run provider tests and verify RED**

Run: `cd backend && pytest tests/test_telegram_provider.py -q`

Expected: imports fail because the Bot API provider does not exist.

- [ ] **Step 3: Implement Bot API client and strict factory**

```python
class TelegramBotAPIProvider:
    def _post(self, method: str, payload: dict) -> dict:
        try:
            response = self.client.post(f"https://api.telegram.org/bot{self.token}/{method}", json=payload, timeout=10.0)
            response.raise_for_status()
            body = response.json()
        except Exception as error:
            raise TelegramProviderError("Telegram Bot API request failed.") from error
        if not body.get("ok"):
            raise TelegramProviderError("Telegram Bot API rejected the request.")
        return body["result"]
```

- [ ] **Step 4: Write webhook secret, idempotency, and workflow tests**

```python
def test_webhook_rejects_wrong_secret(api_client, connection):
    response = api_client.post(f"/api/v1/telegram/webhook/{connection.id}/", TELEGRAM_UPDATE, format="json", HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN="wrong")
    assert response.status_code == 403

def test_webhook_is_idempotent_and_creates_one_update(api_client, connection, settings):
    settings.TELEGRAM_WEBHOOK_SECRET = "expected"
    first = api_client.post(..., HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN="expected")
    second = api_client.post(..., HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN="expected")
    assert first.status_code == second.status_code == 200
    assert TelegramUpdate.objects.filter(connection=connection, update_id="10001").count() == 1
```

- [ ] **Step 5: Run webhook tests and verify RED**

Run: `cd backend && pytest tests/test_telegram_webhook.py -q`

Expected: 404 because the webhook route does not exist.

- [ ] **Step 6: Implement constant-time webhook validation and ingestion**

```python
if not secrets.compare_digest(request.headers.get("X-Telegram-Bot-Api-Secret-Token", ""), settings.TELEGRAM_WEBHOOK_SECRET):
    return api_error("invalid_webhook_secret", "Webhook authentication failed.", status=403)
```

Map `message.chat.id`, `message.from.id`, display name, and text into the existing workflow only for active, approved, monitored chats. Persist the update before processing and return HTTP 200 for unsupported events.

- [ ] **Step 7: Add owner/admin test and webhook registration endpoints**

```python
provider = get_telegram_provider()
identity = provider.get_me()
return Response({"state": "connected", "bot": {"id": str(identity["id"]), "username": identity.get("username", "")}})
```

- [ ] **Step 8: Run Telegram tests and commit**

Run: `cd backend && pytest tests/test_telegram_provider.py tests/test_telegram_webhook.py -q`

Expected: all tests pass.

```bash
git add backend/apps/telegram_integration backend/config/settings.py backend/tests/test_telegram_provider.py backend/tests/test_telegram_webhook.py .env.example
git commit -m "feat: add official Telegram Bot API integration"
```


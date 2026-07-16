# Architecture

The MVP is a monorepo with a Django REST backend and a Vite React frontend.

Backend responsibilities:

- Tenant and role foundation in `accounts` and `workspaces`.
- Product and trigger configuration in `products` and `triggers`.
- Mock Telegram ingestion in `telegram_integration`.
- Mock and Vertex AI provider boundary in `ai_engine`.
- Ethical workflow orchestration in `opportunities.services`.
- Consent, conversations, leads, audit logs, and analytics in domain apps.

Frontend responsibilities:

- Authenticated dashboard shell.
- Simulator-driven demo workflow.
- Operational pages for Telegram, opportunities, approvals, conversations, leads, products, triggers, and analytics.

External systems are isolated behind provider functions:

- `get_ai_provider()`
- `get_telegram_provider()`

This keeps the consent-first workflow independent from the concrete AI or Telegram implementation.

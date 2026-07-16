# API

Base path: `/api/v1/`

Main MVP endpoints:

- `POST /auth/login/`
- `GET /auth/me/`
- `GET /workspaces/`
- `GET /products/`
- `GET /triggers/`
- `GET /telegram/connections/`
- `GET /telegram/chats/`
- `POST /telegram/simulate-message/`
- `GET /opportunities/`
- `GET /approvals/`
- `POST /approvals/{draft_id}/approve/`
- `GET /conversations/`
- `POST /conversations/{conversation_id}/simulate-consent/`
- `POST /conversations/{conversation_id}/generate-product-response/`
- `GET /leads/`
- `POST /leads/convert/`
- `PATCH /leads/{lead_id}/`
- `GET /analytics/overview/`

Errors use:

```json
{
  "error": {
    "code": "consent_required",
    "message": "Consent is required before product information can be sent.",
    "fields": {}
  }
}
```

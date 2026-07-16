# Ethical Dialogue AI

Ethical Dialogue AI is a consent-first Telegram lead discovery SaaS MVP. It monitors authorized Telegram conversations, detects relevant needs, drafts transparent permission requests, records consent, and converts interested contacts into leads.

## Quick Start

```bash
cp .env.example .env
docker compose up --build
```

Local URLs:

- Frontend: http://localhost:5173
- Landing page: http://localhost:5174
- Backend API: http://localhost:8000/api/v1
- API docs: http://localhost:8000/api/docs/

Demo credentials:

- Email: `owner@example.com`
- Password: `ChangeMe123!`

## Local Without Docker

```bash
python3.12 -m venv .venv
. .venv/bin/activate
pip install -r backend/requirements/dev.txt
cd backend
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

## Frontend Apps

This repo contains two independent frontend apps.

### Admin Dashboard

```bash
cd frontend
npm install
npm run dev
```

The admin dashboard runs on `http://localhost:5173` and contains the authenticated workspace dashboard plus the staff-only `/app/superadmin` area.

### Landing Page

```bash
cd landing
npm install
npm run dev
```

The landing page runs on `http://localhost:5174`. Set `VITE_ADMIN_URL` when the landing app should link to a deployed admin dashboard instead of the local `/signin` path.

## Demo Flow

1. Sign in.
2. Open Simulator.
3. Submit: `Can anyone recommend a simple CRM for a small sales team?`
4. Open Approval Queue and approve the permission request.
5. Open Conversations and simulate consent.
6. Generate the product response.
7. Open Leads and convert the consented conversation.
8. Update lead status and review Analytics.

## AI Mode

Local development uses `AI_PROVIDER=mock`. Production path uses platform-managed Google Vertex AI:

```env
AI_PROVIDER=vertex
VERTEX_PROJECT_ID=your-project
VERTEX_LOCATION=us-central1
VERTEX_MODEL=gemini-2.5-flash
GOOGLE_APPLICATION_CREDENTIALS=/run/secrets/google-credentials.json
```

Customer-provided AI credentials are intentionally deferred.

## Telegram Mode

Local development uses `TELEGRAM_PROVIDER=mock`. The backend is organized so an official Telegram Bot API provider can replace the mock provider without changing the workflow services.

## Verification

```bash
cd backend && pytest -q
cd frontend && npm test
cd frontend && npm run build
cd landing && npm test
cd landing && npm run build
docker compose config
```

## Known Limitations

- Real Telegram Bot API webhook setup is scaffolded but not fully enabled.
- Vertex provider validates configuration and shares the provider interface; deterministic local behavior uses mock AI.
- Billing models exist, but real payment processing is deferred.
- OpenAPI generation works but has serializer warnings for some APIView endpoints.

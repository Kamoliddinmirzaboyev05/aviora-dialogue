# Testing

Backend:

```bash
cd backend
pytest -q
```

Frontend:

```bash
cd frontend
npm run build
```

Covered backend behavior:

- login and workspace isolation;
- idempotent seed data;
- trigger matching;
- mock AI and safety checks;
- complete demo workflow API;
- consent-required product response protection;
- Telegram token exclusion from API responses.

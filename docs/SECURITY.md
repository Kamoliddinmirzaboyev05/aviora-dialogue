# Security

Implemented MVP controls:

- JWT authentication.
- Workspace-scoped list/detail APIs.
- Backend consent enforcement before product responses.
- Telegram token field excluded from normal API responses.
- Audit logs for opportunity creation and draft approval.
- No bulk promotional sending features.
- Local secrets ignored by git.

Production requirements:

- Rotate any credentials shared during setup.
- Use a strong `DJANGO_SECRET_KEY`.
- Store Telegram and AI credentials outside git.
- Put TLS in front of the app.
- Add request rate limiting at Nginx and application level.
- Replace local SQLite with PostgreSQL.

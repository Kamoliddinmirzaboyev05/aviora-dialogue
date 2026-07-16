# Deployment

The local MVP is Docker Compose ready. Production deployment should use:

- `docker-compose.prod.yml`
- Nginx reverse proxy
- Gunicorn for Django
- static frontend assets served by an Nginx frontend container
- Celery worker and beat
- PostgreSQL
- Redis
- environment-managed secrets

Do not put credentials in git.

VPS outline:

```bash
scp -r . root@SERVER:/opt/ethical-dialogue-ai
ssh root@SERVER
cd /opt/ethical-dialogue-ai
cp .env.example .env
vim .env
docker compose -f docker-compose.prod.yml up --build -d
docker compose -f docker-compose.prod.yml exec backend python manage.py migrate
docker compose -f docker-compose.prod.yml exec backend python manage.py seed_demo
```

If port 80 is already used on the VPS, set `HTTP_PORT=8080` in `.env` and open `http://SERVER:8080`.

Credentials shared in chat should be rotated after initial setup.

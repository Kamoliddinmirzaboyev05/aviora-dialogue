# Local Setup

Recommended:

```bash
cp .env.example .env
docker compose up --build
```

Manual backend:

```bash
python3.12 -m venv .venv
. .venv/bin/activate
pip install -r backend/requirements/dev.txt
cd backend
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Manual frontend:

```bash
cd frontend
npm install
npm run dev
```

Demo login:

- `owner@example.com`
- `ChangeMe123!`

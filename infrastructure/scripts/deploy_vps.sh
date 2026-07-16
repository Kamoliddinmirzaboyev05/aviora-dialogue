#!/usr/bin/env bash
set -euo pipefail

SERVER="${1:?Usage: deploy_vps.sh root@server}"
APP_DIR="${APP_DIR:-/opt/ethical-dialogue-ai}"

rsync -az --delete \
  --exclude .git \
  --exclude .venv \
  --exclude node_modules \
  --exclude frontend/dist \
  ./ "$SERVER:$APP_DIR/"

ssh "$SERVER" "cd $APP_DIR && test -f .env || cp .env.example .env"
ssh "$SERVER" "cd $APP_DIR && docker compose -f docker-compose.prod.yml up --build -d"
ssh "$SERVER" "cd $APP_DIR && docker compose -f docker-compose.prod.yml exec -T backend python manage.py migrate"

echo "Deployment finished. Review $APP_DIR/.env on the server before enabling real integrations."

# Telegram Setup

Local MVP:

- `TELEGRAM_PROVIDER=mock`
- Mock connection is created by `python manage.py seed_demo`.
- Simulator posts to `/api/v1/telegram/simulate-message/`.

Production direction:

1. Create an official Telegram bot.
2. Store the bot token encrypted at rest.
3. Configure a webhook with a secret.
4. Select only authorized chats for monitoring.
5. Keep manual approval or monitoring-only mode as the default.

The product does not implement unofficial userbot scraping or bulk spam.

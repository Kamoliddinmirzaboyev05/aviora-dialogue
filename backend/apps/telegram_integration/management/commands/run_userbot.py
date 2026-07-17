from django.core.management.base import BaseCommand

from apps.telegram_integration.userbot.worker import main


class Command(BaseCommand):
    help = "Run the Telethon userbot worker (listens to groups and DMs)."

    def handle(self, *args, **options):
        main()

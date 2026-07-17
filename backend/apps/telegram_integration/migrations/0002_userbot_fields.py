from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("telegram_integration", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="telegramconnection",
            name="mode",
            field=models.CharField(default="bot_api", max_length=16),
        ),
        migrations.AddField(
            model_name="telegramconnection",
            name="phone",
            field=models.CharField(blank=True, max_length=32),
        ),
        migrations.AddField(
            model_name="telegramconnection",
            name="session_string",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="telegramconnection",
            name="phone_code_hash",
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AddField(
            model_name="telegramconnection",
            name="login_state",
            field=models.CharField(default="idle", max_length=16),
        ),
        migrations.AddField(
            model_name="telegramconnection",
            name="auto_reply",
            field=models.BooleanField(default=True),
        ),
    ]

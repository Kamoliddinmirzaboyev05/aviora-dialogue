from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("telegram_integration", "0002_userbot_fields"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="telegramconnection",
            index=models.Index(
                fields=["mode", "login_state", "is_active"],
                name="tg_conn_mode_state_idx",
            ),
        ),
    ]

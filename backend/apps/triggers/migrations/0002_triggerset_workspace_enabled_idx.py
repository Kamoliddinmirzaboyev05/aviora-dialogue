from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("triggers", "0001_initial"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="triggerset",
            index=models.Index(fields=["workspace", "enabled"], name="triggerset_ws_enabled_idx"),
        ),
    ]

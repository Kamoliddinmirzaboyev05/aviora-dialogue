from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0001_initial"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="product",
            index=models.Index(fields=["workspace", "status"], name="product_ws_status_idx"),
        ),
    ]

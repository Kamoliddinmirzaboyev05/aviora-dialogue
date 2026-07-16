from django.db import models

from apps.common.models import WorkspaceScopedModel


class Product(WorkspaceScopedModel):
    name = models.CharField(max_length=180)
    short_description = models.TextField()
    target_customer = models.CharField(max_length=255, blank=True)
    problems_solved = models.TextField(blank=True)
    benefits = models.TextField(blank=True)
    pricing_model = models.CharField(max_length=120, blank=True)
    starting_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=8, default="USD")
    website = models.URLField(blank=True)
    booking_link = models.URLField(blank=True)
    status = models.CharField(max_length=32, default="active")

    class Meta:
        constraints = [models.UniqueConstraint(fields=["workspace", "name"], name="unique_product_per_workspace")]

    def __str__(self):
        return self.name

from rest_framework import serializers

from apps.common.serializers import WorkspaceScopedSerializerMixin
from apps.products.models import Product


class ProductSerializer(WorkspaceScopedSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"

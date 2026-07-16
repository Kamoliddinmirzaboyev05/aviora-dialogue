from rest_framework import serializers

from apps.telegram_integration.models import TelegramChat, TelegramConnection


class TelegramConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramConnection
        exclude = ["encrypted_bot_token"]


class TelegramChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramChat
        fields = "__all__"

from rest_framework import serializers
from .models import Tariff, Subscription


class TariffSerializer(serializers.ModelSerializer):
    """
    Serializer for Tariff model.

    Represents a subscription plan with its title, duration, cost, and trial status.
    """

    title = serializers.CharField(
        help_text="Название тарифного плана, отображаемое пользователям."
    )

    days_count = serializers.IntegerField(
        help_text="Количество дней действия подписки по этому тарифу."
    )

    is_trial = serializers.BooleanField(
        help_text="Является ли этот тариф пробным (бесплатным)."
    )

    cost = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Стоимость подписки в тенге."
    )

    created_at = serializers.DateTimeField(
        read_only=True,
        help_text="Дата и время создания тарифа."
    )

    updated_at = serializers.DateTimeField(
        read_only=True,
        help_text="Дата и время последнего обновления тарифа."
    )

    class Meta:
        model = Tariff
        fields = [
            'id',
            'title',
            'days_count',
            'is_trial',
            'cost',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Serializer for Subscription model.

    Represents a user's active subscription with tariff details and expiration date.
    """

    tariff = serializers.PrimaryKeyRelatedField(
        read_only=True,
        help_text="ID тарифного плана, на который оформлена подписка."
    )

    tariff_title = serializers.CharField(
        source='tariff.title',
        read_only=True,
        help_text="Название тарифного плана."
    )

    tariff_days_count = serializers.IntegerField(
        source='tariff.days_count',
        read_only=True,
        help_text="Количество дней действия тарифа."
    )

    deadline = serializers.DateTimeField(
        help_text="Дата и время окончания подписки."
    )

    created_at = serializers.DateTimeField(
        read_only=True,
        help_text="Дата и время создания подписки."
    )

    is_active = serializers.BooleanField(
        read_only=True,
        help_text="Активна ли подписка на текущий момент."
    )

    class Meta:
        model = Subscription
        fields = [
            'id',
            'tariff',
            'tariff_title',
            'tariff_days_count',
            'deadline',
            'created_at',
            'is_active'
        ]
        read_only_fields = ['id', 'deadline', 'created_at', 'is_active']

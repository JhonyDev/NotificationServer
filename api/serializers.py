from rest_framework import serializers
from .models import NotificationPriority, Notification


class NotificationPrioritySerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPriority
        # fields = ('fixture_id', 'full_time_result')
        fields = '__all__'

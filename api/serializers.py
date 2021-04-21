from rest_framework import serializers
from .models import NotificationPriority, Users, NotificationStatus


class NotificationPrioritySerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPriority
        # fields = ('fixture_id', 'full_time_result')
        fields = '__all__'


class NotificationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationStatus
        # fields = ('fixture_id', 'full_time_result')
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'

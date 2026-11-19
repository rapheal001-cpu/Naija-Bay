from rest_framework import serializers
from accounts.models import Notifications


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notifications
        fields = '__all__'

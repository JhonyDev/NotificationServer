from django.contrib import admin
from .models import Notification, NotificationPriority

admin.site.register(Notification)
admin.site.register(NotificationPriority)

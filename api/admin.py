from django.contrib import admin
from .models import Notification, NotificationPriority, CronLogs, Users

admin.site.register(Notification)
admin.site.register(NotificationPriority)
admin.site.register(CronLogs)
admin.site.register(Users)

from django.contrib import admin
from .models import SentNotification, NotificationPriority, CronLogs, Users

admin.site.register(SentNotification)
admin.site.register(NotificationPriority)
admin.site.register(CronLogs)
admin.site.register(Users)

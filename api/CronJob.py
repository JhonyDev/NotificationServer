from .models import CronLogs


def weekly_notification_cronjob():
    cron = CronLogs()
    cron.save()

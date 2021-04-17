from .models import CronLogs


def weekly_notification_cronjob():
    cron = CronLogs('some new cron')
    cron.save()


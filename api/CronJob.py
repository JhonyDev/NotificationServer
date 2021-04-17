from .models import CronLogs


def weekly_notification_cronjob():
    cron = CronLogs()
    cron.log_time = 'new cron'
    cron.save()

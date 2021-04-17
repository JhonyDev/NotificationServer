from .models import CronLogs


def my_cron_job():
    cron = CronLogs()
    cron.log_time = 'cron job inside'
    cron.save()

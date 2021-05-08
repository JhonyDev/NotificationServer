import datetime

from .models import Fixtures, CronLogs
from .notification_utils import check_for_updates
import time


def my_cron_job():
    fixtures = list(Fixtures.objects.all())
    for fixture in fixtures:
        print('fixtures -------- ' + fixture.get_fixture_id())
        check_for_updates(fixture.get_fixture_id())


def run_cron():
    my_cron_job()
    time_stamp = str(datetime.datetime.now())
    cron_log = CronLogs()
    cron_log.log_time = time_stamp
    cron_log.save()

    time.sleep(10)
    my_cron_job()

    time.sleep(10)
    my_cron_job()

    time.sleep(10)
    my_cron_job()

    time.sleep(10)
    my_cron_job()

    time.sleep(10)
    my_cron_job()

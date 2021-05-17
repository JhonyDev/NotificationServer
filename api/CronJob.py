import datetime
import time

from .models import Fixtures, CronLogs
from .notification_utils import check_for_updates

time_delay = 15
loop_count = int(50 / time_delay)


def my_cron_job():
    fixtures = list(Fixtures.objects.all())
    for fixture in fixtures:
        print('fixtures -------- ' + fixture.get_fixture_id())
        check_for_updates(fixture.get_fixture_id())


def run_cron_with(delay):
    cron = CronLogs()
    cron.log_time = str(datetime.datetime.now())
    cron.save()
    time.sleep(delay)
    my_cron_job()


def run_cron():
    my_cron_job()
    for x in range(3):
        run_cron_with(time_delay)

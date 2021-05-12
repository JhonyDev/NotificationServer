import datetime

from .models import Fixtures
from .notification_utils import check_for_updates
import time

time_delay = 6
loop_count = int(60 / time_delay)


def my_cron_job():
    fixtures = list(Fixtures.objects.all())
    for fixture in fixtures:
        print('fixtures -------- ' + fixture.get_fixture_id())
        check_for_updates(fixture.get_fixture_id())


def run_cron_with(delay):
    time.sleep(delay)
    my_cron_job()


def run_cron():
    my_cron_job()
    for x in range(loop_count):
        run_cron_with(time_delay)

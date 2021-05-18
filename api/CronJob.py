import datetime
import time

from .models import Fixtures, CronLogs
from .notification_utils import check_for_updates

time_delay = 15
loop_count = int(290 / time_delay)


def my_cron_job(is_once_in_min):
    if is_once_in_min:
        fixtures = list(Fixtures.objects.all())
        for fixture in fixtures:
            fixture.is_live = True
            fixture.save()
        crons = CronLogs.objects.all()
        for cron in crons:
            cron.delete()

    cron = CronLogs()
    cron.log_time = str(datetime.datetime.now())
    cron.save()
    fixtures = list(Fixtures.objects.all())
    for fixture in fixtures:
        if not fixture.is_live:
            continue
        print('fixtures -------- ' + fixture.get_fixture_id())
        check_for_updates(fixture.get_fixture_id())


def run_cron_with(delay):
    time.sleep(delay)
    my_cron_job(False)


def run_cron():
    my_cron_job(True)
    for x in range(loop_count):
        run_cron_with(time_delay)

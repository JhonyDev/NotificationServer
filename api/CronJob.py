import datetime

from .models import Fixtures, CronLogs
from .utils import check_for_updates


def my_cron_job(is_running_cron):
    if is_running_cron:
        time_stamp = str(datetime.datetime.now())
        cron_log = CronLogs()
        cron_log.log_time = time_stamp
        cron_log.save()

    fixtures = list(Fixtures.objects.all())
    for fixture in fixtures:
        print('fixtures -------- ' + fixture.get_fixture_id())
        check_for_updates(fixture.get_fixture_id())


def run_cron():
    my_cron_job(True)

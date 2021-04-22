from .models import Fixtures
from .utils import check_for_updates


def my_cron_job():
    fixtures = list(Fixtures.objects.all())
    for fixture in fixtures:
        print('fixtures -------- ' + fixture.get_fixture_id())
        check_for_updates(fixture.get_fixture_id())

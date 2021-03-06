import time

from django.http import HttpResponse
from firebase_admin import messaging
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .CronJob import run_cron
from .models import NotificationPriority, NotificationStatus, CronLogs, Fixtures
from .serializers import NotificationPrioritySerializer


def current_milli_time():
    return round(time.time() * 1000)


@api_view(['POST', ])
def api_post_notification_priority(request2):
    new_notification_priority = NotificationPriority()
    serializer = NotificationPrioritySerializer(new_notification_priority, data=request2.data)
    notification_status = NotificationStatus()
    if serializer.is_valid():
        delete_notification_priority = list(NotificationPriority.objects.filter(
            fixture_id=new_notification_priority.get_fixture_id(), user_id=new_notification_priority.get_user_id()))
        for notification_priority in delete_notification_priority:
            notification_priority.delete()
        serializer.save()
        notification_status.notification_id = new_notification_priority.notification_id
        notification_status.save()
        fixture = Fixtures()
        fixture.fixture_id = new_notification_priority.get_fixture_id()
        fixture.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def test(request2):
    stri = ''
    fixtures = list(Fixtures.objects.filter(is_live=True))
    for fixture in fixtures:
        stri += fixture.fixture_id + '<br>'
    return HttpResponse(stri)


def send_notification(request2):
    stri = ''

    nps = NotificationPriority.objects.all()

    registration_tokens = []
    for np in nps:
        stri += np.user_id + '<br>'
        registration_tokens.append(np.user_id)

    stri += str(registration_tokens) + '<br>'

    message = messaging.MulticastMessage(
        notification=messaging.Notification(title="title",
                                            body="subtitle",
                                            ),
        tokens=registration_tokens
    )
    messaging.send_multicast(message)
    return HttpResponse(stri)


def print_crons(request2):
    crons = CronLogs.objects.all()
    stri = ''
    for s in crons:
        stri += s.log_time + ' <br>'

    return HttpResponse(stri)


def run_crons(request2):
    stri = ''
    run_cron()
    return HttpResponse(stri)

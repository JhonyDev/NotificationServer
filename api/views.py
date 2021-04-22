import json

from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests

from .models import Users, NotificationPriority, NotificationStatus, Fixtures
from .serializers import UserSerializer, NotificationPrioritySerializer
from .CronJob import my_cron_job


@api_view(['POST', ])
def api_post_user_id(request):
    user = Users()
    serializer = UserSerializer(user, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', ])
def api_post_notification_priority(request):
    notification_priority = NotificationPriority()
    serializer = NotificationPrioritySerializer(notification_priority, data=request.data)
    notification_status = NotificationStatus()
    if serializer.is_valid():
        delete_notification_priority = list(NotificationPriority.objects.filter(
            fixture_id=notification_priority.get_fixture_id(), user_id=notification_priority.get_user_id()))
        for notification_priority in delete_notification_priority:
            notification_priority.delete()
        serializer.save()
        notification_status.notification_id = notification_priority.notification_id
        notification_status.save()
        fixture = Fixtures()
        fixture.fixture_id = notification_priority.get_fixture_id()
        fixture.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def test(request):
    notifications = list(NotificationPriority.objects.all())
    fixtures = list(Fixtures.objects.all())
    for notification in notifications:
        fixture_inserted = False
        for fixture in fixtures:
            if fixture.get_fixture_id() == notification.get_fixture_id():
                fixture_inserted = True
                continue
            fixture = Fixtures()
            fixture.fixture_id = notification.get_fixture_id()
            fixture.save()
            fixture_inserted = True
        if not fixture_inserted:
            fixture = Fixtures()
            fixture.fixture_id = notification.get_fixture_id()
            fixture.save()
    my_cron_job()
    return HttpResponse('Cron Initiated')

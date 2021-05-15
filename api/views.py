import datetime

from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .CronJob import my_cron_job
from .models import Users, NotificationPriority, NotificationStatus, Fixtures
from .serializers import UserSerializer, NotificationPrioritySerializer


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
    new_notification_priority = NotificationPriority()
    serializer = NotificationPrioritySerializer(new_notification_priority, data=request.data)
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


def test(request):
    my_cron_job()
    time_stamp = str(datetime.datetime.now())
    return HttpResponse('Cron Initiated ' + time_stamp)

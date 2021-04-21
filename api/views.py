import json

from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests

from .models import Users, NotificationPriority, NotificationStatus
from .serializers import UserSerializer, NotificationPrioritySerializer, NotificationStatusSerializer
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

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def test(request):
    response_str = ''
    url = 'https://api-football-v1.p.rapidapi.com/v2/fixtures/id/653088'

    headers = {'Accept': 'application/json',
               'content-type': 'application/json',
               'x-rapidapi-key': '9bc6e8bddamshfc5efe4660335c5p1254e0jsnb8f0b64ef59e',
               'x-rapidapi-host': 'api-football-v1.p.rapidapi.com'}

    r = requests.get(url, headers=headers)
    json_object = json.loads(r.content)
    fixture_item = json_object['api']['fixtures']
    first_half_result = fixture_item[0]['score'].get('halftime')
    second_half_result = fixture_item[0]['score'].get('fulltime')
    my_cron_job()
    return HttpResponse(first_half_result + ' ' + second_half_result)

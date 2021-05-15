import datetime
import time

from django.http import HttpResponse
from flask import Flask, jsonify, request
from pusher_push_notifications import PushNotifications
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .CronJob import my_cron_job
from .models import NotificationPriority, NotificationStatus, Fixtures
from .serializers import NotificationPrioritySerializer

beams_client = PushNotifications(
    instance_id='1889a652-be8c-4e56-aed1-04bedd6eff47',
    secret_key='6274C8792B95D8C0A54DBE48ABFF7807DEEF94C6EFA83518E676280272254356',
)
app = Flask(__name__)


def current_milli_time():
    return round(time.time() * 1000)


@api_view(['GET', ])
def api_post_user_id(request2):
    with app.app_context():
        user_id = str(current_milli_time())
        user_id_in_query_param = request.args.get('user_id')
        print('###############' + user_id_in_query_param)
        if user_id != user_id_in_query_param:
            return 'Inconsistent request', 401

        beams_token = beams_client.generate_token(user_id)
        return jsonify(beams_token)


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
    my_cron_job()
    time_stamp = str(datetime.datetime.now())
    return HttpResponse('Cron Initiated ' + time_stamp)

from django.shortcuts import render, get_object_or_404
from flask import Flask, request, jsonify
from pusher_push_notifications import PushNotifications
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import NotificationPriority, CronLogs
from .serializers import NotificationPrioritySerializer
from .CronJob import push_notify
from flask import Flask, jsonify, request
from pusher_push_notifications import PushNotifications

beams_client = PushNotifications(
    instance_id='YOUR_INSTANCE_ID_HERE',
    secret_key='YOUR_SECRET_KEY_HERE',
)

app = Flask(__name__)


class NotificationPriList(APIView):

    def get(self, request):
        pass

    def post(self):
        pass

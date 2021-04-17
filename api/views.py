from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import NotificationPriority, CronLogs
from .serializers import NotificationPrioritySerializer


class NotificationPriList(APIView):
    print('This is some testing text')
    cron_log = CronLogs()
    cron_log.log_time = 'some log time'
    cron_log.save()

    def get(self, request):
        stocks = NotificationPriority.objects.all()
        serializer = NotificationPrioritySerializer(stocks, many=True)
        return Response(serializer.data)

    def post(self):
        pass

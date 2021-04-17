from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import NotificationPriority
from .serializers import NotificationPrioritySerializer


class NotificationPriList(APIView):

    def get(self, request):
        stocks = NotificationPriority.objects.all()
        serializer = NotificationPrioritySerializer(stocks, many=True)
        return Response(serializer.data)

    def post(self):
        pass

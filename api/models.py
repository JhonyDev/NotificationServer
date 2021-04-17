from django.db import models


class NotificationPriority(models.Model):
    fixture_id = models.CharField(max_length=250)
    full_time_result = models.CharField(max_length=50)
    half_time_result = models.CharField(max_length=50)
    kick_off = models.CharField(max_length=50)
    red_cards = models.CharField(max_length=50)
    yellow_cards = models.CharField(max_length=50)
    goals = models.CharField(max_length=50)


class Notification(models.Model):
    notification_id = models.CharField(max_length=50)
    user_token = models.CharField(max_length=500)
    fixture_id = models.CharField(max_length=250)
    notification_status = models.CharField(max_length=50)


class Users(models.Model):
    user_token = models.CharField(max_length=50)


class CronLogs(models.Model):
    log_time = models.CharField(max_length=100)

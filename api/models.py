from django.db import models

from api import info


class NotificationPriority(models.Model):
    first_notification = models.CharField(max_length=10, default=info.first)
    user_id = models.CharField(max_length=250, default='no_user')
    fixture_id = models.IntegerField()
    full_time_result = models.IntegerField()
    half_time_result = models.IntegerField()
    kick_off = models.IntegerField()
    red_cards = models.IntegerField()
    yellow_cards = models.IntegerField()
    goals = models.IntegerField()
    notification_id = models.CharField(max_length=250, default=0)
    objects = models.Manager()

    def get_first(self):
        return self.first_notification

    def set_first(self, first_str):
        self.first_notification = first_str

    def get_fixture_id(self):
        return self.fixture_id

    def get_user_id(self):
        return self.user_id

    def get_notification_id(self):
        return self.notification_id

    def get_half_time_result(self):
        return self.half_time_result

    def __int__(self):
        return self.fixture_id


class Fixtures(models.Model):
    fixture_id = models.CharField(max_length=20, primary_key=True)
    objects = models.Manager()

    def get_fixture_id(self):
        return self.fixture_id


class NotificationQueue(models.Model):
    title = models.CharField(max_length=15)
    subtitle = models.CharField(max_length=30)
    user = models.CharField(max_length=50)
    objects = models.Manager()

    def get_title(self):
        return self.title

    def get_subtitle(self):
        return self.subtitle

    def get_user(self):
        return self.user


class SentNotification(models.Model):
    title = models.CharField(max_length=50)
    subtitle = models.CharField(max_length=50)
    user = models.CharField(max_length=50)
    objects = models.Manager()

    def get_title(self):
        return self.title

    def get_subtitle(self):
        return self.subtitle

    def get_user(self):
        return self.user


class Users(models.Model):
    user_token = models.CharField(max_length=50)
    objects = models.Manager()

    def get_user_token(self):
        return self.user_token


class CronLogs(models.Model):
    log_time = models.CharField(max_length=100)
    objects = models.Manager()


class NotificationStatus(models.Model):
    notification_id = models.CharField(max_length=250, default=0)
    notification_status = models.CharField(max_length=10, default=info.NOT_SENT)
    objects = models.Manager()

    def get_notification_status(self):
        return self.notification_status

    def set_notification_status(self, status):
        self.notification_status = status

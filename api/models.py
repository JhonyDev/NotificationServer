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

    def get_fixture_id(self):
        return self.fixture_id

    def get_user_id(self):
        return self.user_id

    def get_notification_id(self):
        return self.notification_id

    def get_full_time_result(self):
        return self.full_time_result

    def get_half_time_result(self):
        return self.half_time_result

    def get_kick_off(self):
        return self.kick_off

    def get_red_cards(self):
        return self.red_cards

    def get_yellow_cards(self):
        return self.yellow_cards

    def get_goals(self):
        return self.goals

    def __int__(self):
        return self.fixture_id


class Fixtures(models.Model):
    fixture_id = models.CharField(max_length=20, primary_key=True)
    is_live = models.BooleanField(default=True)
    objects = models.Manager()

    def get_fixture_id(self):
        return self.fixture_id


class NotificationQueue(models.Model):
    notification_type = models.CharField(max_length=70)
    subtitle = models.CharField(max_length=70)
    user = models.CharField(max_length=70)
    title = models.CharField(max_length=50, default='-')
    fixture = models.CharField(max_length=20, default='-')
    objects = models.Manager()

    def get_notification_type(self):
        return self.notification_type

    def get_fixture(self):
        return self.fixture

    def get_subtitle(self):
        return self.subtitle

    def get_title(self):
        return self.title

    def get_user(self):
        return self.user


class SentNotification(models.Model):
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=100)
    user = models.CharField(max_length=500)
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
    log_time = models.CharField(max_length=1000)
    objects = models.Manager()


class NotificationStatus(models.Model):
    notification_id = models.CharField(max_length=250, default=0)
    notification_status = models.CharField(max_length=10, default=info.NOT_SENT)
    objects = models.Manager()

    def get_notification_status(self):
        return self.notification_status

    def set_notification_status(self, status):
        self.notification_status = status

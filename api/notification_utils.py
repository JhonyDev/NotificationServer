import datetime
import json

import firebase_admin
import requests
from firebase_admin import credentials, messaging

from api import info
from .models import NotificationPriority, NotificationQueue, SentNotification, Fixtures

cred = credentials.Certificate(
    "/home/jj/NotificationServer/football-11cf0-firebase-adminsdk-cxs9t-7c068c318c.json")
firebase_admin.initialize_app(cred)

is_first = info.not_first


def push_notify(title, subtitle, user_id):
    global is_first
    if is_first == info.first:
        add_to_sent_notifications(title, subtitle, user_id)
        return

    notification = list(SentNotification.objects.filter(title=title, subtitle=subtitle, user=user_id))
    if notification:
        return

    notify(user_id, title, subtitle)
    add_to_sent_notifications(title, subtitle, user_id)


def add_to_sent_notifications(title, subtitle, user_id):
    notification = SentNotification()
    notification.title = title
    notification.subtitle = subtitle
    notification.user = user_id
    notification.save()


def add_notification_to_queue(notification_type, subtitle, user_id, title, fixture):
    queue = NotificationQueue()
    queue.notification_type = notification_type
    queue.title = title
    queue.fixture = fixture
    queue.subtitle = subtitle
    queue.user = user_id
    queue.save()

    print('event notification contained')


def notify(user_id, title, subtitle):
    registration_tokens = [user_id]
    message = messaging.MulticastMessage(
        notification=messaging.Notification(title=title,
                                            body=subtitle,
                                            ),
        tokens=registration_tokens
    )
    messaging.send_multicast(message)


def full_time_notification(fixture_item, user_id):
    print(fixture_item.get('score'))
    if fixture_item.get('score').get('fulltime', None) is not None:
        title = 'Full Time'
        subtitle = fixture_item.get('homeTeam').get('team_name') + ' ' + str(fixture_item.get('score').get('fulltime'))
        subtitle += ' ' + fixture_item.get('awayTeam').get('team_name')
        push_notify(title, subtitle, user_id)


def half_time_notification(fixture_item, user_id):
    print(fixture_item.get('score'))
    if fixture_item['status'] == 'Halftime':
        title = 'Half Time'
        subtitle = fixture_item.get('homeTeam').get('team_name') + ' ' + str(fixture_item.get('score').get('halftime'))
        subtitle += ' ' + fixture_item.get('awayTeam').get('team_name')
        push_notify(title, subtitle, user_id)


def kick_off_notification(fixture_item, user_id):
    if fixture_item.get('status') == 'First Half':
        title = 'Kick Off'
        subtitle = fixture_item.get('homeTeam').get('team_name') + ' v ' + fixture_item.get('awayTeam').get(
            'team_name')
        push_notify(title, subtitle, user_id)


def red_card_notification(fixture_item, user_id):
    events = fixture_item.get('events')
    subtitle = fixture_item.get('homeTeam').get('team_name') + ' v ' + fixture_item.get('awayTeam').get('team_name')
    if events is None:
        return
    for event in events:
        if event.get('detail') == info.RED_CARD:
            elapsed_time = str(event.get('elapsed'))
            title = 'RED CARD - ' + elapsed_time + ' min'
            push_notify(title, subtitle, user_id)


def yellow_card_notification(fixture_item, user_id):
    events = fixture_item.get('events')
    subtitle = fixture_item.get('homeTeam').get('team_name') + ' v ' + fixture_item.get('awayTeam').get('team_name')
    if events is None:
        return
    for event in events:
        if event.get('detail') == info.YELLOW_CARD:
            elapsed_time = str(event.get('elapsed'))
            title = 'Yellow Card - ' + elapsed_time + ' min'
            push_notify(title, subtitle, user_id)


def goal_notification(fixture_item, user_id):
    events = fixture_item.get('events')
    subtitle = fixture_item.get('homeTeam').get('team_name') + ' v ' + fixture_item.get('awayTeam').get('team_name')

    if events is None:
        return

    for event in events:
        if event.get('type') == 'Goal':
            print(event)
            elapsed_time = str(event.get('elapsed'))
            title = 'Goal - ' + elapsed_time + ' min'
            push_notify(title, subtitle, user_id)


def check_if_in_priority(param, fixture_item, user_id, notification_priority):
    if param == info.FULL_TIME:
        if notification_priority.get_full_time_result() == 1:
            full_time_notification(fixture_item, user_id)

    if param == info.HALF_TIME:
        if notification_priority.get_half_time_result() == 1:
            half_time_notification(fixture_item, user_id)

    if param == info.KICK_OFF:
        if notification_priority.get_kick_off() == 1:
            kick_off_notification(fixture_item, user_id)

    if param == info.RED_CARDS:
        if notification_priority.get_red_cards() == 1:
            fixture_item['redCards'] = fixture_item.get('redCards', 0) + 1
            red_card_notification(fixture_item, user_id)

    if param == info.YELLOW_CARDS:
        if notification_priority.get_yellow_cards() == 1:
            fixture_item['yellowCards'] = fixture_item.get('yellowCards', 0) + 1
            yellow_card_notification(fixture_item, user_id)

    if param == info.GOALS:
        if notification_priority.get_goals() == 1:
            goal_notification(fixture_item, user_id)


def init(fixture_item, user_id, notification_priority):
    fixture_item = fixture_item[0]

    check_if_in_priority(info.HALF_TIME, fixture_item, user_id, notification_priority)
    check_if_in_priority(info.FULL_TIME, fixture_item, user_id, notification_priority)
    check_if_in_priority(info.KICK_OFF, fixture_item, user_id, notification_priority)
    check_if_in_priority(info.YELLOW_CARDS, fixture_item, user_id, notification_priority)
    check_if_in_priority(info.RED_CARDS, fixture_item, user_id, notification_priority)
    check_if_in_priority(info.GOALS, fixture_item, user_id, notification_priority)


def is_in_time(current_time_api, target_time_api):
    target_time_api = target_time_api.replace('+00:00', 'Z')

    now = datetime.datetime.strptime(current_time_api, "%Y-%m-%dT%H:%M:%SZ")
    target_time = datetime.datetime.strptime(target_time_api, "%Y-%m-%dT%H:%M:%SZ")

    def is_in_range(def_hour, minute):
        return def_hour == target_time.hour and minute == target_time.minute

    is_time = False
    for x in range(10):
        if now.minute + x >= 60:
            check_hour = (now.hour + 1) % 24
            check_minute = (now.minute + x) % 60
            is_time = is_in_range(check_hour, check_minute)
        else:
            check_hour = now.hour
            check_minute = now.minute + x
            is_time = is_in_range(check_hour, check_minute)

        if is_time:
            break

    return is_time


def check_for_updates(fixture_id):
    if len(fixture_id) < 4:
        return

    url = 'https://v2.api-football.com/fixtures/id/' + str(fixture_id)
    headers = {'Accept': 'application/json',
               'content-type': 'application/json',
               'x-apisports-key': 'af4532daada823806464862dc4e8e435',
               'x-rapidapi-host': 'api-football-v1.p.rapidapi.com'}

    r = requests.get(url, headers=headers)
    json_object = json.loads(r.content)
    fixture_item = json_object.get('api')

    fixture = Fixtures.objects.get(fixture_id=fixture_id)

    if not fixture_item:
        print('---No API')
        print(json_object)
        fixture.is_live = False
        fixture.save()
        return

    fixture_item = fixture_item.get('fixtures')
    if not fixture_item:
        print('---No Fixture')
        print(fixture_item)
        fixture.is_live = False
        fixture.save()
        return

    notification_priority_list = NotificationPriority.objects.filter(fixture_id=fixture_id)
    for notification_priority in notification_priority_list:

        if notification_priority.get_full_time_result() == 0 and notification_priority.get_half_time_result(
        ) == 0 and notification_priority.get_kick_off(
        ) == 0 and notification_priority.get_red_cards(
        ) == 0 and notification_priority.get_yellow_cards(
        ) == 0 and notification_priority.get_goals(
        ) == 0:

            notification_priority.delete()
            priorities = list(NotificationPriority.objects.filter(user_id=notification_priority.user_id,
                                                                  fixture_id=notification_priority.fixture_id))
            for priority in priorities:
                priority.delete()

        global is_first
        is_first = notification_priority.first_notification

        init(fixture_item, notification_priority.get_user_id(), notification_priority)

        if notification_priority.first_notification == info.first:
            notification_priority.first_notification = info.not_first
            notification_priority.save()

        if fixture_item[0].get('status') == 'Match Finished' or fixture_item[0].get('status') == 'Match Postponed' or \
                fixture_item[0].get('status') == 'Match Cancelled':
            notification_priority.delete()

    fixture = Fixtures.objects.get(fixture_id=fixture_id)
    if fixture_item[0].get('status') == 'Match Finished' or fixture_item[0].get('status') == 'Match Postponed' or \
            fixture_item[0].get('status') == 'Match Cancelled':
        fixture.delete()
    elif fixture_item[0].get('status') == 'First Half' or fixture_item[0].get('status') == 'Halftime' or \
            fixture_item[0].get('status') == 'Second Half':
        fixture.is_live = True
    else:
        current_time_api = datetime.datetime.today().strftime('%Y-%m-%dT%H:%M:%SZ')
        target_time_api = fixture_item[0].get('event_date')
        fixture.is_live = is_in_time(current_time_api, target_time_api)

    fixture.save()

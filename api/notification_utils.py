import json

from pusher_push_notifications import PushNotifications
import requests
from .models import NotificationPriority, NotificationQueue, SentNotification, Fixtures
from api import info

is_first = info.not_first


def push_notify(title, subtitle, user_id):
    notification = SentNotification.objects.filter(title=title, subtitle=subtitle, user=user_id)
    global is_first
    print('------>>>>>> GLOBAL ' + is_first + ' <<<<<<---------')
    if notification:
        print('notification already sent')
        return

    if is_first != info.first:
        print('published notification')
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
    beams_client = PushNotifications(
        instance_id='1889a652-be8c-4e56-aed1-04bedd6eff47',
        secret_key='6274C8792B95D8C0A54DBE48ABFF7807DEEF94C6EFA83518E676280272254356',
    )
    response = beams_client.publish_to_interests(
        interests=[user_id],
        publish_body={
            'apns': {
                'aps': {
                    'alert': 'alert!'
                }
            },
            'fcm': {
                'notification': {
                    'title': title,
                    'body': subtitle
                }
            }
        }
    )
    print(user_id)
    print(response)


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
    if 0 <= fixture_item.get('elapsed') <= 5:
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
            sent_notification = SentNotification.objects.filter(user=user_id, subtitle=subtitle, title=title)
            if not sent_notification:
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
            sent_notification = SentNotification.objects.filter(title=title, subtitle=subtitle, user=user_id)
            if not sent_notification:
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
            sent_notification = SentNotification.objects.filter(title=title, subtitle=subtitle, user=user_id)

            if not sent_notification:
                push_notify(title, subtitle, user_id)


def check_if_in_priority(param, fixture_id, fixture_item, user_id):
    notification_priorities = NotificationPriority.objects.filter(user_id=user_id, fixture_id=fixture_id)
    for notification_priority in notification_priorities:
        if not notification_priority:
            return

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
        break


def init(fixture_item, user_id, fixture_id):
    fixture_item = fixture_item[0]

    check_if_in_priority(info.HALF_TIME, fixture_id, fixture_item, user_id)
    check_if_in_priority(info.FULL_TIME, fixture_id, fixture_item, user_id)
    check_if_in_priority(info.KICK_OFF, fixture_id, fixture_item, user_id)
    check_if_in_priority(info.YELLOW_CARDS, fixture_id, fixture_item, user_id)
    check_if_in_priority(info.RED_CARDS, fixture_id, fixture_item, user_id)
    check_if_in_priority(info.GOALS, fixture_id, fixture_item, user_id)


def check_for_updates(fixture_id):
    url = 'https://v2.api-football.com/fixtures/id/' + str(fixture_id)
    headers = {'Accept': 'application/json',
               'content-type': 'application/json',
               'x-apisports-key': 'af4532daada823806464862dc4e8e435',
               'x-rapidapi-host': 'api-football-v1.p.rapidapi.com'}

    r = requests.get(url, headers=headers)
    json_object = json.loads(r.content)
    fixture_item = json_object.get('api')

    if not fixture_item:
        print('---No API')
        print(json_object)
        return

    fixture_item = fixture_item.get('fixtures')
    if not fixture_item:
        print('---No Fixture')
        print(fixture_item)
        return
    notification_priority_list = NotificationPriority.objects.filter(fixture_id=fixture_id)
    for notification_priority in notification_priority_list:
        first_priority = notification_priority.get_first()
        print('#####--->>>>>' + first_priority)
        global is_first
        is_first = notification_priority.get_first()
        notification_priority.first_notification = info.not_first
        notification_priority.save()
        init(fixture_item, notification_priority.get_user_id(), fixture_id)
        if fixture_item[0].get('status') == 'Match Finished':
            notification_priority.delete()

    if fixture_item[0].get('status') == 'Match Finished':
        fixture = Fixtures.objects.get(fixture_id=fixture_id)
        fixture.delete()

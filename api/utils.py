import json

from pusher_push_notifications import PushNotifications
import requests
from .models import NotificationPriority, NotificationStatus, SentNotification, Fixtures
from api import info


def push_notify(title, subtitle, user_id):
    notification = SentNotification.objects.filter(title=title, subtitle=subtitle, user=user_id)
    if notification:
        return
    notification = SentNotification()
    notification.title = title
    notification.subtitle = subtitle
    notification.user = user_id

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

    print('Notification Sent to ----->>>>' + user_id)
    print(response)
    notification.save()


def full_time_notification(fixture_item, user_id):
    if fixture_item.get('status') == info.MATCH_FINISHED:
        notification = NotificationPriority.objects.filter(fixture_id=fixture_item.get('fixture_id'), user_id=user_id)
        notification.delete()
        return
    title = 'Full Time'
    subtitle = fixture_item.get('homeTeam').get('team_name') + ' ' + str(fixture_item.get('goalsHomeTeam'))
    subtitle += '-' + str(fixture_item.get('goalsAwayTeam')) + ' ' + fixture_item.get('awayTeam').get('team_name')
    push_notify(title, subtitle, user_id)


def half_time_notification(fixture_item, user_id):
    if fixture_item.get('status') == info.MATCH_FINISHED:
        notification = NotificationPriority.objects.filter(fixture_id=fixture_item.get('fixture_id'), user_id=user_id)
        notification.delete()
        return
    title = 'Half Time'
    subtitle = fixture_item.get('homeTeam').get('team_name') + ' ' + str(fixture_item.get('goalsHomeTeam'))
    subtitle += '-' + str(fixture_item.get('goalsAwayTeam')) + ' ' + fixture_item.get('awayTeam').get('team_name')
    push_notify(title, subtitle, user_id)


def kick_off_notification(fixture_item, user_id):
    if fixture_item.get('status') == info.MATCH_FINISHED:
        notification = NotificationPriority.objects.filter(fixture_id=fixture_item.get('fixture_id'), user_id=user_id)
        notification.delete()
        return
    title = 'Kick Off'
    subtitle = fixture_item.get('homeTeam').get('team_name') + ' v ' + fixture_item.get('awayTeam').get('team_name')
    push_notify(title, subtitle, user_id)


def red_card_notification(fixture_item, user_id):
    if fixture_item.get('status') == info.MATCH_FINISHED:
        notification = NotificationPriority.objects.filter(fixture_id=fixture_item.get('fixture_id'), user_id=user_id)
        notification.delete()
        return
    subtitle = fixture_item.get('homeTeam').get('team_name') + ' v ' + fixture_item.get('awayTeam').get('team_name')
    events = fixture_item.get('events')
    event_index = 0
    elapsed_time = ''
    for event in events:
        if event.get('detail') == info.RED_CARD:
            elapsed_time = str(event.get('elapsed'))
            break
        event_index += 1
    title = 'Red Card - ' + elapsed_time + ' min'
    push_notify(title, subtitle, user_id)


def yellow_card_notification(fixture_item, user_id):
    if fixture_item.get('status') == info.MATCH_FINISHED:
        notification = NotificationPriority.objects.filter(fixture_id=fixture_item.get('fixture_id'), user_id=user_id)
        notification.delete()
        return
    events = fixture_item.get('events')
    event_index = 0
    elapsed_time = '-'
    for event in events:
        if event.get('detail') == info.YELLOW_CARD:
            elapsed_time = str(event.get('elapsed'))
            break
        event_index += 1
    title = 'Yellow Card - ' + elapsed_time + ' min'
    subtitle = fixture_item.get('homeTeam').get('team_name') + ' v ' + fixture_item.get('awayTeam').get('team_name')
    push_notify(title, subtitle, user_id)


def goal_notification(fixture_item, user_id):
    if fixture_item.get('status') == info.MATCH_FINISHED:
        notification = NotificationPriority.objects.filter(fixture_id=fixture_item.get('fixture_id'), user_id=user_id)
        notification.delete()
        return
    events = fixture_item.get('events')
    elapsed_time = ''
    for event in events:
        if event.get('type') == info.GOAL:
            elapsed_time = str(event.get('elapsed'))
            break
    title = 'Goal - ' + elapsed_time + ' min'
    subtitle = fixture_item.get('homeTeam').get('team_name') + ' v ' + fixture_item.get('awayTeam').get('team_name')
    push_notify(title, subtitle, user_id)


def check_if_in_priority(param, fixture_id, fixture_item, user_id):
    notification_priorities = NotificationPriority.objects.filter(user_id=user_id).filter(fixture_id=fixture_id)
    for notification_priority in notification_priorities:

        if not notification_priority:
            return

        if param == info.FULL_TIME:
            if notification_priority.full_time_result == 1:
                full_time_notification(fixture_item, user_id)

        if param == info.HALF_TIME:
            if notification_priority.get_half_time_result() == 1:
                half_time_notification(fixture_item, user_id)

        if param == info.KICK_OFF:
            if notification_priority.get_half_time_result() == 1:
                kick_off_notification(fixture_item, user_id)

        if param == info.RED_CARDS:
            if notification_priority.get_half_time_result() == 1:
                fixture_item['redCards'] = fixture_item.get('redCards', 0) + 1
                red_card_notification(fixture_item, user_id)

        if param == info.YELLOW_CARDS:
            if notification_priority.get_half_time_result() == 1:
                fixture_item['yellowCards'] = fixture_item.get('yellowCards', 0) + 1
                yellow_card_notification(fixture_item, user_id)

        if param == info.GOALS:
            if notification_priority.get_half_time_result() == 1:
                goal_notification(fixture_item, user_id)
        break


def init_first_half_notification(fixture_item, first_half, fixture_id, user_id):
    if first_half == '':
        return
    if (90 / 2 + 11) > int(fixture_item['elapsed']) > (90 / 2):
        check_if_in_priority(info.HALF_TIME, fixture_id, fixture_item, user_id)


def init_second_half_notification(fixture_item, second_half_result, fixture_id, user_id, notification_id):
    if not second_half_result:
        return
    notification_statuses = NotificationStatus.objects.filter(notification_id=notification_id)
    for notification_status in notification_statuses:
        if not notification_status:
            return
        if not notification_status:
            return
        if notification_status.get_notification_status() == info.SENT:
            return
        notification_status.set_notification_status(info.SENT)
        check_if_in_priority(info.FULL_TIME, fixture_id, fixture_item, user_id)
        break


def init_match_started(fixture_item, fixture_id, user_id):
    if fixture_item.get('elapsed') < 11 and fixture_item.get('status') == info.MATCH_STARTED:
        check_if_in_priority(info.KICK_OFF, fixture_id, fixture_item, user_id)


def init_event_notification(fixture_item, fixture_id, user_id):
    events_list = fixture_item.get('events')
    if not events_list:
        return

    for event in events_list:
        if event.get('type') == info.CARD:
            if event.get('detail') == info.YELLOW_CARD:
                check_if_in_priority(info.YELLOW_CARDS, fixture_id, fixture_item, user_id)
            if event.get('detail') == info.RED_CARD:
                check_if_in_priority(info.RED_CARDS, fixture_id, fixture_item, user_id)
        if event.get('type') == info.GOAL:
            check_if_in_priority(info.GOALS, fixture_id, fixture_item, user_id)


def init(fixture_item, user_id, notification_id, fixture_id):
    fixture_item = fixture_item[0]
    first_half_result = fixture_item['score'].get('halftime', '')
    second_half_result = fixture_item['score'].get('fulltime', '')

    init_first_half_notification(fixture_item, first_half_result, fixture_id, user_id)

    init_second_half_notification(fixture_item, second_half_result, fixture_id, user_id, notification_id)

    init_match_started(fixture_item, fixture_id, user_id)

    if fixture_item.get('events', '') == '':
        print('---No events')
        return

    init_event_notification(fixture_item, fixture_id, user_id)


def check_for_updates(fixture_id):
    url = 'https://api-football-v1.p.rapidapi.com/v2/fixtures/id/' + str(fixture_id)
    headers = {'Accept': 'application/json',
               'content-type': 'application/json',
               'x-rapidapi-key': '9bc6e8bddamshfc5efe4660335c5p1254e0jsnb8f0b64ef59e',
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
        init(fixture_item, notification_priority.get_user_id(), notification_priority.get_notification_id(), fixture_id)

    if fixture_item.get('status') == 'Match Finished':
        fixture = Fixtures.objects.get(fixture_id=fixture_id)
        fixture.delete()

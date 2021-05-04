import json

from pusher_push_notifications import PushNotifications
import requests
from .models import NotificationPriority, NotificationQueue, SentNotification, Fixtures
from api import info


def push_notify(title, subtitle, user_id, notification_type):
    notification = SentNotification.objects.filter(title=title, subtitle=subtitle, user=user_id)
    global is_first
    print('------>>>>>> GLOBAL ' + is_first + ' <<<<<<---------')
    if notification:
        print('notification already sent')
        return

    if is_first == info.first:
        if notification_type == info.FULL_TIME or notification_type == info.HALF_TIME or notification_type == info.KICK_OFF:
            print('first so not sent')
            add_to_sent_notifications(title, subtitle, user_id)
        else:
            print('Added event to queue')
            add_notification_to_queue(notification_type, subtitle, user_id, title)
    else:
        print('published notification')
        notify(user_id, title, subtitle)
        add_to_sent_notifications(title, subtitle, user_id)
        if notification_type == info.FULL_TIME or notification_type == info.HALF_TIME or notification_type == info.KICK_OFF:
            pass
        else:
            print('sending notifications in queue')
            notification_queues = list(
                NotificationQueue.objects.filter(notification_type=notification_type, user=user_id))
            for notification_queue in notification_queues:
                notification = SentNotification.objects.filter(title=title, subtitle=subtitle, user=user_id)
                if notification:
                    return
                add_to_sent_notifications(notification_queue.get_title(), notification_queue.get_subtitle(),
                                          notification_queue.get_user())
                notify(notification_queue.get_user(), notification_queue.get_title(),
                       notification_queue.get_subtitle(), )


def add_to_sent_notifications(title, subtitle, user_id):
    notification = SentNotification()
    notification.title = title
    notification.subtitle = subtitle
    notification.user = user_id
    notification.save()


def add_notification_to_queue(notification_type, subtitle, user_id, title):
    queue = NotificationQueue()
    queue.notification_type = notification_type
    queue.title = title
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
    if fixture_item.get('score').get('fulltime') is not None and fixture_item.get('elapsed') < (90 / 2) + 2:
        title = 'Full Time'
        subtitle = fixture_item.get('homeTeam').get('team_name') + ' ' + str(fixture_item.get('goalsHomeTeam'))
        subtitle += '-' + str(fixture_item.get('goalsAwayTeam')) + ' ' + fixture_item.get('awayTeam').get('team_name')
        push_notify(title, subtitle, user_id, info.FULL_TIME)


def half_time_notification(fixture_item, user_id):
    if fixture_item.get('score').get('halftime') is not None and fixture_item.get('elapsed') < (90 / 2) + 2:
        title = 'Half Time'
        subtitle = fixture_item.get('homeTeam').get('team_name') + ' ' + str(fixture_item.get('goalsHomeTeam'))
        subtitle += '-' + str(fixture_item.get('goalsAwayTeam')) + ' ' + fixture_item.get('awayTeam').get('team_name')
        push_notify(title, subtitle, user_id, info.HALF_TIME)


def kick_off_notification(fixture_item, user_id):
    if fixture_item.get('elapsed') < 2 and fixture_item.get('status') == 'Match Started':
        title = 'Kick Off'
        subtitle = fixture_item.get('homeTeam').get('team_name') + ' v ' + fixture_item.get('awayTeam').get('team_name')
        push_notify(title, subtitle, user_id, info.KICK_OFF)


def red_card_notification(fixture_item, user_id):
    events = fixture_item.get('events')
    subtitle = fixture_item.get('homeTeam').get('team_name') + ' v ' + fixture_item.get('awayTeam').get('team_name')
    title = ''
    for event in events:
        if event.get('detail') == info.RED_CARD:
            elapsed_time = str(event.get('elapsed'))
            title = 'RED CARD - ' + elapsed_time + ' min'
            sent_notification = SentNotification.objects.filter(user=user_id, subtitle=subtitle, title=title)
            if sent_notification:
                continue
            break
    push_notify(title, subtitle, user_id, info.RED_CARDS)


def yellow_card_notification(fixture_item, user_id):
    events = fixture_item.get('events')
    subtitle = fixture_item.get('homeTeam').get('team_name') + ' v ' + fixture_item.get('awayTeam').get('team_name')
    title = ''
    for event in events:
        if event.get('detail') == info.YELLOW_CARD:
            elapsed_time = str(event.get('elapsed'))
            title = 'Yellow Card - ' + elapsed_time + ' min'
            sent_notification = SentNotification.objects.filter(user=user_id, subtitle=subtitle, title=title)
            if sent_notification:
                continue
            break
    push_notify(title, subtitle, user_id, info.YELLOW_CARDS)


def goal_notification(fixture_item, user_id):
    events = fixture_item.get('events')
    subtitle = fixture_item.get('homeTeam').get('team_name') + ' v ' + fixture_item.get('awayTeam').get('team_name')
    title = ''
    for event in events:
        if event.get('type') == info.GOAL:
            elapsed_time = str(event.get('elapsed'))
            title = 'Goal - ' + elapsed_time + ' min'
            sent_notification = SentNotification.objects.filter(user=user_id, subtitle=subtitle, title=title)
            if sent_notification:
                continue
            break

    push_notify(title, subtitle, user_id, info.GOALS)


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


def init(fixture_item, user_id, fixture_id):
    fixture_item = fixture_item[0]

    check_if_in_priority(info.HALF_TIME, fixture_id, fixture_item, user_id)
    check_if_in_priority(info.FULL_TIME, fixture_id, fixture_item, user_id)
    check_if_in_priority(info.KICK_OFF, fixture_id, fixture_item, user_id)

    init_event_notification(fixture_item, fixture_id, user_id)


is_first = info.not_first


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
        first_priority = notification_priority.get_first()
        print('#####--->>>>>' + first_priority)
        global is_first
        is_first = notification_priority.get_first()
        init(fixture_item, notification_priority.get_user_id(), fixture_id)
        notification_priority.first_notification = info.not_first
        notification_priority.save()

    if fixture_item[0].get('status') == 'Match Finished':
        fixture = Fixtures.objects.get(fixture_id=fixture_id)
        fixture.delete()

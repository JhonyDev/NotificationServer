from .models import CronLogs


def push_notify(title):
    print('inside from cronjob')
    from pusher_push_notifications import PushNotifications

    beams_client = PushNotifications(
        instance_id='1889a652-be8c-4e56-aed1-04bedd6eff47',
        secret_key='6274C8792B95D8C0A54DBE48ABFF7807DEEF94C6EFA83518E676280272254356',
    )
    response = beams_client.publish_to_interests(
        interests=['hello'],
        publish_body={
            'apns': {
                'aps': {
                    'alert': 'Hello!'
                }
            },
            'fcm': {
                'notification': {
                    'title': title,
                    'body': 'Hello, World!'
                }
            }
        }
    )
    cron = CronLogs()
    cron.log_time = response['publishId']
    cron.save()


def my_cron_job():
    push_notify('running cron')

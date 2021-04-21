from .models import Users, NotificationPriority
from .utils import check_for_updates


def my_cron_job():
    user_list = list(Users.objects.all())
    for user in user_list:
        notification_priorities = list(NotificationPriority.objects.filter(user_id=user.get_user_token()))
        for notification_priority in notification_priorities:
            print(user.get_user_token())
            print(notification_priority.get_notification_id)
            check_for_updates(notification_priority.get_fixture_id(), user.get_user_token()
                              , notification_priority.get_notification_id())

    # push_notify(title='', subtitle='', subtitle_2='', notification_id='', user_id='some_user_id')





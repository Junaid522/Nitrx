import datetime

from django.core.paginator import Paginator
from django.utils import timezone

from RestProject.constants import NOTIFICATION_CHUNK
from notifications.models import Notification


class Notifications(object):

    def create_notification(self, actor, notification_type, instance=None):
        notification_instance = Notification(actor=actor, notification_type=notification_type, content_object=instance)
        notification_instance.save()

    def get_notification(self, actor, notification_type, instance=None):
        return Notification.objects.filter(actor=actor, notification_type=notification_type, object_id=instance).first()

    def mark_read(self, notification_id, actor_id):
        notification = Notification.objects.filter(id=notification_id, actor__id=actor_id).first()
        if notification:
            notification.read = True
            notification.save()
        return notification

    def mark_all_read(self, actor_id):
        return Notification.objects.filter(actor__id=actor_id).update(read=True)

    def delete_notification(self, actor_id, notification_id):
        return Notification.objects.filter(actor__id=actor_id, id=notification_id).update(is_valid=False)

    def get_notifications(self, filter_dict):
        notifications = Notification.objects.filter(**filter_dict).exclude(object_id__isnull=True)[:NOTIFICATION_CHUNK]
        return [notification for notification in notifications if notification.content_object]

    def get_chunk_of_notifications(self, filter_dict, page):
        notifications = Notification.objects.filter(**filter_dict).exclude(object_id__isnull=True)

        paginator = Paginator(notifications, NOTIFICATION_CHUNK)
        notifications = paginator.page(page)

        return [notification for notification in notifications if notification.content_object]

    def get_notification_time(self, created_at):
        time = (timezone.make_aware(datetime.datetime.now())) - created_at
        day = time.seconds // (24 * 3600)
        time = time.seconds % (24 * 3600)
        hour = time // 3600
        time %= 3600
        minutes = time // 60
        time %= 60
        seconds = time
        if day:
            return "{}d ago".format(day)
        elif hour:
            return "{}h ago".format(hour)
        elif minutes:
            return "{}m ago".format(minutes)
        return "{}s ago".format(seconds)

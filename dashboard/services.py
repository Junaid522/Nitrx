from django.contrib.sessions.models import Session
from django.utils import timezone

from accounts.models import User


class DashboardService(object):

    def get_logged_in_users(self):
        active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
        user_id_list = []
        for session in active_sessions:
            data = session.get_decoded()
            user_id_list.append(data.get('_auth_user_id', None))
        return User.objects.filter(id__in=user_id_list).count()

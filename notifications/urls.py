from django.urls import path

from . import views

urlpatterns = [
    path('api/notifications/all', views.AllNotificationsView.as_view(), name='all-notifications.'),
    path('api/notifications/read', views.ReadNotificationsView.as_view(), name='read-notifications.'),
    path('api/notifications/delete', views.DeleteNotificationsView.as_view(), name='delete-notifications.'),
    path('api/notifications/mark_all_read', views.MarkAllReadNotificationsView.as_view(), name='mark-all-read.'),
]

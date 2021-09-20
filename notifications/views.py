import math

# Create your views here.
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from RestProject.constants import (NOTIFICATION_CHUNK, NOTIFICATION_READ_SUCCESS, NOTIFICATION_ERROR,
                                   NOTIFICATION_ALL_READ_SUCCESS, NOTIFICATION_DELETE_SUCCESS)
from notifications.models import Notification
from notifications.serializers import NotificationSerializer
from notifications.services import Notifications


class AllNotificationsView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination

    def get_queryset(self):
        filter_dict = {'actor': self.request.user, 'is_valid': True}
        notifications = Notification.objects.filter(**filter_dict).exclude(object_id__isnull=True)

        filtered_notifications = [notification for notification in notifications if notification.content_object]
        unread = len([notification for notification in filtered_notifications if notification.read == False])

        return filtered_notifications, unread

    def list(self, request, *args, **kwargs):
        filtered_notifications, unread = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(filtered_notifications)
        context = {}
        context['user_id'] = request.user.id
        if page is not None:
            serializer = self.serializer_class(page, context=context, many=True)
            total_pages = int((int(math.ceil(len(filtered_notifications) / 10.0)) * 10) / NOTIFICATION_CHUNK)
            return self.get_paginated_response({
                'unread': unread,
                'total_notifications': len(filtered_notifications),
                'total_pages': total_pages,
                'data': serializer.data
            })

        serializer = self.serializer_class(filtered_notifications, context=context, many=True).data
        return Response(serializer)


class ReadNotificationsView(APIView):
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        status = HTTP_400_BAD_REQUEST
        message = NOTIFICATION_ERROR
        if Notifications().mark_read(request.data.get('notification_id'), self.request.user.id):
            status = HTTP_200_OK
            message = NOTIFICATION_READ_SUCCESS
        return Response({"message": message}, status=status)


class DeleteNotificationsView(APIView):
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        status = HTTP_400_BAD_REQUEST
        message = NOTIFICATION_ERROR
        if Notifications().delete_notification(request.data.get('notification_id'), self.request.user.id):
            status = HTTP_200_OK
            message = NOTIFICATION_DELETE_SUCCESS
        return Response({"message": message}, status=status)


class MarkAllReadNotificationsView(APIView):
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        status = HTTP_400_BAD_REQUEST
        message = NOTIFICATION_ERROR
        if Notifications().mark_all_read(self.request.user.id):
            status = HTTP_200_OK
            message = NOTIFICATION_ALL_READ_SUCCESS
        return Response({"message": message}, status=status)

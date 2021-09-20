from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.authentication import SessionAuthentication

from RestProject import settings
from chat_app.serializers import MessageReaderSerializer, MessageModelSerializer, UserModelSerializer
from chat_app.models import MessageModel, Thread
from accounts.models import User


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    SessionAuthentication scheme used by DRF. DRF's SessionAuthentication uses
    Django's session framework for authentication which requires CSRF to be
    checked. In this case we are going to disable CSRF tokens for the API.
    """

    def enforce_csrf(self, request):
        return


class MessagePagination(PageNumberPagination):
    """
    Limit message prefetch to one page.
    """
    page_size = settings.MESSAGES_TO_LOAD


class MessageModelViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, ]
    queryset = MessageModel.objects.all()
    serializer_class = MessageReaderSerializer
    allowed_methods = ('GET', 'POST', 'HEAD', 'OPTIONS')
    pagination_class = MessagePagination

    def list(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(Q(recipient=request.user) |
                                             Q(user=request.user))
        target = self.request.query_params.get('target', None)
        if target is not None:
            self.queryset = self.queryset.filter(
                Q(recipient=request.user, user__username=target) |
                Q(recipient__username=target, user=request.user))
        return super(MessageModelViewSet, self).list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        msg = get_object_or_404(
            self.queryset.filter(Q(recipient=request.user) |
                                 Q(user=request.user),
                                 Q(pk=kwargs['pk'])))
        serializer = self.get_serializer(msg)
        return Response(serializer.data)


class MessageModelPostViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, ]
    queryset = MessageModel.objects.all()
    serializer_class = MessageModelSerializer
    allowed_methods = ('POST',)
    pagination_class = MessagePagination

    def list(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(Q(recipient=request.user) |
                                             Q(user=request.user))
        target = self.request.query_params.get('target', None)
        if target is not None:
            messages = MessageModel.objects.filter(
                Q(recipient=request.user, user__username=target) |
                Q(recipient__username=target, user=request.user))
            for msg in messages:
                msg.read_receipt = True
                msg.save()
            self.queryset = self.queryset.filter(
                Q(recipient=request.user, user__username=target) |
                Q(recipient__username=target, user=request.user))
        return super(MessageModelPostViewSet, self).list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        msg = get_object_or_404(
            self.queryset.filter(Q(recipient=request.user) |
                                 Q(user=request.user),
                                 Q(pk=kwargs['pk'])))
        serializer = self.get_serializer(msg)
        return Response(serializer.data)


class UserModelViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, ]
    queryset = User.objects.all()
    serializer_class = UserModelSerializer
    allowed_methods = ('GET', 'HEAD', 'OPTIONS')
    pagination_class = None  # Get all user

    def list(self, request, *args, **kwargs):
        # Get all users except yourself
        # messaging_users = Thread.objects.filter(Q(user=request.user) | Q(recipient=request.user)).values_list('recipient__id', flat=True)
        messaging_us = Thread.objects.filter(Q(user=request.user) | Q(recipient=request.user))
        user_list = []
        for msg in messaging_us:
            if msg.messagemodel_set.all():
                user_list.append(msg.recipient.id)
        # self.queryset = self.queryset.filter(id__in=messaging_users).exclude(id=request.user.id)
        self.queryset = self.queryset.filter(id__in=user_list).exclude(id=request.user.id)

        # self.queryset = self.queryset.exclude(id=request.user.id)
        return super(UserModelViewSet, self).list(request, *args, **kwargs)

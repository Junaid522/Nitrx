from rest_framework import serializers

from accounts.serializers import FollowUserSerializer
from posts.serializers import PostLikeSerializer, PostCommentSerializer, PostRateSerializer, CommentRateSerializer
from stories.serializers import StoryRateSerializer
from .models import Notification
from .services import Notifications


class NotificationSerializer(serializers.ModelSerializer):
    detail = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ('id', 'notification_type', 'read', 'content_type', 'detail', 'time',)

    def get_detail(self, instance):
        serializer = None
        if instance.notification_type == Notification.LIKE_POST:
            serializer = PostLikeSerializer(instance.content_object).data
        elif instance.notification_type == Notification.COMMENT_POST:
            serializer = PostCommentSerializer(instance.content_object).data
        elif instance.notification_type == Notification.FOLLOWING:
            serializer = FollowUserSerializer(instance.content_object,
                                              context={'user_id': self.context.get('user_id')}).data
        elif instance.notification_type == Notification.RATE_POST:
            serializer = PostRateSerializer(instance.content_object).data
        elif instance.notification_type == Notification.RATE_STORY:
            serializer = StoryRateSerializer(instance.content_object).data
        elif instance.notification_type == Notification.RATE_COMMENT:
            serializer = CommentRateSerializer(instance.content_object).data
        elif instance.notification_type == Notification.MENTION_COMMENT:
            serializer = PostCommentSerializer(instance.content_object,
                                               context={'type': instance.notification_type}).data
        elif instance.notification_type == Notification.REPLY_COMMENT:
            serializer = PostCommentSerializer(instance.content_object,
                                               context={'type': instance.notification_type}).data

        return serializer

    def get_time(self, obj):
        return Notifications().get_notification_time(obj.created_at)

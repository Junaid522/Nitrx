from django.db.models import Q

from accounts.models import User
from django.shortcuts import get_object_or_404
from chat_app.models import MessageModel, Thread
from rest_framework.serializers import ModelSerializer, CharField
from rest_framework import serializers

from common.commmon_services import convert_time_mhr
from posts.models import Post
from posts.serializers import PostDetailSerializer


class MessageModelSerializer(ModelSerializer):
    user = CharField(source='user.username', read_only=True)
    recipient = CharField(source='recipient.username')
    message_type = CharField()

    timestamp = serializers.SerializerMethodField()

    def get_timestamp(self, obj):
        return convert_time_mhr(obj.timestamp)

    def create(self, validated_data):
        if 'user' not in validated_data.keys():
            user = self.context['request'].user
        else:
            user = User.objects.filter(id=validated_data['user']).first()
        recipient = get_object_or_404(
            User, username=validated_data['recipient']['username'])
        if validated_data.get('thread'):
            msg = MessageModel(recipient=recipient,
                               body=validated_data['body'], thread=validated_data.get('thread'),
                               user=user, message_type=validated_data['message_type'])
        else:
            group_name = f'{user.id}-{recipient.id}' if user.id < recipient.id else \
                f'{recipient.id}-{user.id}'
            is_thread_exist = Thread.objects.filter(title=group_name).exists()
            if not is_thread_exist:
                Thread.objects.create(user=user, recipient=recipient, title=group_name)
            thread_obj = Thread.objects.filter(Q(recipient=recipient, user=user) |
                                               Q(recipient=user, user=recipient)).first()
            msg = MessageModel(recipient=recipient,
                               body=validated_data['body'], thread=thread_obj,
                               user=user, message_type=validated_data['message_type'])
        msg.save()
        return msg

    class Meta:
        model = MessageModel
        fields = ('id', 'user', 'recipient', 'timestamp', 'body', 'message_type', 'read_receipt')


class UserModelSerializer(ModelSerializer):
    _id = serializers.IntegerField(source='id')
    avatar = serializers.URLField(source="image")
    name = serializers.SerializerMethodField()
    message = serializers.SerializerMethodField()

    def get_name(self, obj):
        return '{} {}'.format(obj.first_name, obj.last_name)

    def get_message(self, obj):
        data = {}
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
            message = MessageModel.objects.filter(Q(user=obj, recipient=user) | Q(recipient=obj, user=user)).last()
            if message:
                data['body'] = message.body
                data['time'] = convert_time_mhr(message.timestamp)
                data['type'] = message.message_type
                data['read_receipt'] = message.read_receipt
                return data
            else:
                return ''

    class Meta:
        model = User
        fields = ('username', 'name', '_id', 'avatar', 'username', 'first_name', 'last_name', 'message')


class MessageReaderSerializer(serializers.ModelSerializer):
    _id = serializers.IntegerField(source='id')
    current_user = UserModelSerializer(source='user')
    user = UserModelSerializer(source='recipient')
    text = serializers.CharField(source='body')
    createdAt = serializers.SerializerMethodField()
    post_detail = serializers.SerializerMethodField()
    read_receipt = serializers.SerializerMethodField()

    def get_createdAt(self, obj):
        return convert_time_mhr(obj.timestamp)

    def get_post_detail(self, obj):
        if obj.message_type == MessageModel.POST_URL:
            id = obj.body.split('?id=')[1]
            return PostDetailSerializer(Post.objects.filter(id=id).first()).data
        else:
            return None

    def get_read_receipt(self, obj):
        if not obj.read_receipt:
            obj.read_receipt = True
            obj.save()
        return obj.read_receipt

    class Meta:
        model = MessageModel
        fields = ('current_user', 'user', '_id', 'text', 'createdAt', 'message_type', 'post_detail', 'read_receipt')


class ThreadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Thread
        fields = '__all__'
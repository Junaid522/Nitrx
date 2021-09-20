# chat/consumers.py
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import json

from accounts.models import User
from chat_app.models import Thread, MessageModel
from chat_app.serializers import MessageModelSerializer, ThreadSerializer
from common.commmon_services import convert_time_mhr


def check_is_thread_exists(group_name):
    return Thread.objects.filter(title=group_name).exists()


def create_thread(group_name, user_id, other_user_id):
    return Thread.objects.create(title=group_name, user=User.objects.filter(id=user_id).first(),
                                 recipient=User.objects.filter(id=other_user_id).first())


def get_thread_users(title):
    thread = Thread.objects.filter(title=title).first()
    return {'user': thread.user, 'recipient': thread.recipient}


def get_thread(group_name):
    thread = Thread.objects.filter(title=group_name).first()
    return {'thread': thread}


def get_user(id):
    return User.objects.filter(id=id).first()


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        user_id = self.scope["user_id"]
        other_user_id = self.scope["other_user"]
        self.group_name = f'{user_id[0]}-{other_user_id}' if user_id[0] < other_user_id else \
            f'{other_user_id}-{user_id[0]}'
        is_thread_available = await sync_to_async(check_is_thread_exists)(self.group_name)
        if not is_thread_available:
            await sync_to_async(create_thread)(self.group_name, user_id[0], other_user_id)
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        type = text_data_json['type']
        data = {}
        data['body'] = text_data_json['message']
        users = await sync_to_async(get_thread_users)(self.group_name)
        data['user'] = self.scope['user_id']
        rec = await sync_to_async(get_user)(self.scope['other_user'])
        data['recipient'] = {'username': rec.username}
        data['message_type'] = type
        thread = await sync_to_async(get_thread)(self.group_name)
        data['thread'] = thread.get('thread')
        message_serializer = MessageModelSerializer()
        new_message = await sync_to_async(message_serializer.create)(data)
        message = {}
        message['_id'] = new_message.id
        message['current_user'] = {}
        message['current_user']['_id'] = new_message.user.id
        message['current_user']['username'] = new_message.user.username
        message['current_user']['name'] = new_message.user.first_name + ' ' + new_message.user.last_name
        message['current_user']['avatar'] = new_message.user.image_url
        message['user'] = {}
        message['user']['_id'] = new_message.recipient.id
        message['user']['username'] = new_message.recipient.username
        message['user']['name'] = new_message.recipient.first_name + ' ' + new_message.recipient.last_name
        message['user']['avatar'] = new_message.recipient.image_url
        # message['recipient'] = new_message.recipient.username
        message['text'] = new_message.body
        message['message_type'] = new_message.message_type
        message['createdAt'] = convert_time_mhr(new_message.timestamp)
        message['read_receipt'] = new_message.read_receipt
        # Send message to room group
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'message',
                'message': message
            }
        )

    async def message(self, event):
        message = event['message']
        await self.send(
            text_data=json.dumps({
                'message': message
            }))

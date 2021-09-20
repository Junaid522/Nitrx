from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import models

from accounts.models import User
from common.models import BaseModel


class Thread(BaseModel):
    title = models.CharField(max_length=5)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='user',
                             related_name='thread_from_user', db_index=True)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='recipient',
                                  related_name='thread_to_user', db_index=True)

    def __str__(self):
        return self.title


class MessageModel(models.Model):
    """
    This class represents a chat message. It has a owner (user), timestamp and
    the message body.

    """
    TEXT = 'text'
    POST_URL = 'post_url'
    STORY_URL = 'story_url'
    FILE = 'file'
    AUDIO = 'audio'
    MESSAGE_TYPE = (
        (TEXT, 'Text'),
        (FILE, 'File'),
        (POST_URL, 'Post URL'),
        (STORY_URL, 'Story URL'),
        (AUDIO, 'Audio'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='user',
                             related_name='from_user', db_index=True)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='recipient',
                                  related_name='to_user', db_index=True)
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, null=True, blank=True)
    timestamp = models.DateTimeField('timestamp', auto_now_add=True, editable=False,
                                     db_index=True)
    body = models.TextField('body')

    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPE, default=TEXT)
    file_url = models.URLField(null=True, blank=True)
    read_receipt = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)

    def characters(self):
        """
        Toy function to count body characters.
        :return: body's char number
        """
        return len(self.body)

    def notify_ws_clients(self):
        """
        Inform client there is a new message.
        """
        notification = {
            'type': 'message',
            'message': '{}'.format(self.id)
        }

        channel_layer = get_channel_layer()
        print("user.id {}".format(self.user.id))
        print("user.id {}".format(self.recipient.id))

        async_to_sync(channel_layer.group_send)("{}".format(self.user.id), notification)
        async_to_sync(channel_layer.group_send)("{}".format(self.recipient.id), notification)

    def save(self, *args, **kwargs):
        """
        Trims white spaces, saves the message and notifies the recipient via WS
        if the message is new.
        """
        new = self.id
        self.body = self.body.strip()  # Trimming whitespaces from the body
        super(MessageModel, self).save(*args, **kwargs)
        if new is None:
            self.notify_ws_clients()

    # Meta
    class Meta:
        verbose_name_plural = 'messages'
        ordering = ('timestamp',)

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

# Create your models here.
from accounts.models import User
from common.models import BaseModel


class Notification(BaseModel):
    MENTION_COMMENT = 'mention_comment'
    FOLLOWING = 'following'
    LIKE_POST = 'like_post'
    COMMENT_POST = 'comment_post'
    RATE_COMMENT = 'rate_comment'
    REPLY_COMMENT = 'reply_comment'
    RATE_POST = 'rate_post'
    RATE_STORY = 'rate_story'
    CHAT_STARTED = 'chat_started'
    GROUP_CHAT_ADD = 'group_chat_add'

    NOTIFICATION_TYPE = (
        (MENTION_COMMENT, 'Mention Comment'),
        (FOLLOWING, 'Following'),
        (LIKE_POST, 'Like Post'),
        (COMMENT_POST, 'Comment Post'),
        (RATE_STORY, 'Rate Story'),
        (RATE_POST, 'Rate Post'),
        (RATE_COMMENT, 'Rate Comment'),
        (REPLY_COMMENT, 'Reply Comment'),
        (CHAT_STARTED, 'Chat Started'),
        (GROUP_CHAT_ADD, 'Group Chat Add'),
    )

    actor = models.ForeignKey(User, on_delete=models.CASCADE, )
    notification_type = models.CharField(max_length=250, choices=NOTIFICATION_TYPE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    read = models.BooleanField(default=False)

    def __str__(self):
        return '%s %s' % (self.actor.username, self.read)

    class Meta:
        ordering = ['-id', ]

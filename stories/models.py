from django.db import models
# Create your models here.
from django.db.models import QuerySet
from django_group_by import GroupByMixin

from accounts.models import User
from common.models import BaseModel


class StoryQuerySet(QuerySet, GroupByMixin):
    pass


class Story(BaseModel):
    IMAGE = 'IMAGE'
    VIDEO = 'VIDEO'
    STORY_CHOICES = (
        (VIDEO, 'VIDEO'),
        (IMAGE, 'IMAGE'),
    )
    objects = StoryQuerySet.as_manager()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expire_at = models.DateTimeField(null=True, blank=True)
    file = models.FileField(upload_to='static/story_files', max_length=254, null=True, blank=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    story_url = models.CharField(max_length=255, blank=True, null=True)
    url = models.TextField(null=True, blank=True)
    story_type = models.CharField(max_length=20, choices=STORY_CHOICES, default=IMAGE)

    def __str__(self):
        return self.user.username


class StoryView(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    story = models.ForeignKey(Story, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class StoryRating(BaseModel):
    ONE = '1'
    THREE = '3'
    FIVE = '5'
    SEVEN = '7'
    TEN = '10'
    RATE_TYPE = (
        (ONE, 1),
        (THREE, 3),
        (FIVE, 5),
        (SEVEN, 7),
        (TEN, 10),
    )
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    user_rated = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATE_TYPE)

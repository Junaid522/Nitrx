from django.db import models

from accounts.models import User
from categories.models import Category
from common.models import BaseModel


class PostMaterial(BaseModel):
    IMAGE = 'IMAGE'
    VIDEO = 'VIDEO'
    POST_CHOICES = (
        (VIDEO, 'VIDEO'),
        (IMAGE, 'IMAGE'),
    )
    url = models.TextField(null=True, blank=True)
    post_type = models.CharField(max_length=20, choices=POST_CHOICES, default=IMAGE)

    def __str__(self):
        return self.post_type + "-" + self.url


class Post(BaseModel):
    title = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    keywords = models.CharField(max_length=20, blank=True, null=True)
    image = models.FileField(upload_to='static/post_images', max_length=254, null=True, blank=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    media_files = models.ManyToManyField(PostMaterial)
    website = models.CharField(max_length=255, null=True, blank=True)
    post_qr = models.FileField(upload_to='static/post_qr_codes/', blank=True, null=True)

    def __str__(self):
        return self.title


class PostLike(BaseModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user_liked = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.post.title


class PostImpressions(BaseModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user_impressed = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.post.title


class PostView(BaseModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user_view = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.post.title


class PostComment(BaseModel):
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user_commented = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    mentioned_users = models.ManyToManyField(User, null=True, blank=True, related_name="mentioned_users")

    def __str__(self):
        return self.post.title


class CommentRating(BaseModel):
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
    comment = models.ForeignKey(PostComment, on_delete=models.CASCADE)
    user_rated = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATE_TYPE)

    def __str__(self):
        return self.comment.post.title


class PostSave(BaseModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.post.title


class PostRating(BaseModel):
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
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user_rated = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATE_TYPE)

    def __str__(self):
        return self.post.title


class BlacklistPost(BaseModel):
    SPAM = 'SPAM'
    INAPPROPRIATE = 'INAPPROPRIATE'
    REPORT_TYPE = (
        (SPAM, "SPAM"),
        (INAPPROPRIATE, "INAPPROPRIATE"),
    )
    user_reported = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    report = models.CharField(choices=REPORT_TYPE, default=SPAM, max_length=25)

    def __str__(self):
        return self.post.title

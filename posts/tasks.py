
from celery import shared_task

from accounts.models import User
from posts.models import Post, PostImpressions


@shared_task
def save_impressions(post_ids, user_id):
    for post in Post.objects.filter(id__in=post_ids):
        post_object = Post.objects.filter(id=post.id).first()
        user = User.objects.filter(id=user_id).first()
        PostImpressions.objects.get_or_create(post=post_object, user_impressed=user)

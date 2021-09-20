from django.db.models import Q

from accounts.services import UserManagement
from categories.models import SelectedCategories
from posts.models import Post, BlacklistPost, PostLike, PostRating, PostComment, CommentRating


class PostManagement(object):

    def get_user_posts(self, user):
        return Post.objects.filter(creator=user, is_valid=True)

    def get_reported_posts(self, user):
        return BlacklistPost.objects.filter(is_valid=True, user_reported=user).values_list('post__id', flat=True)

    def get_non_reported_posts(self, users, self_user):
        return Post.objects.filter(is_valid=True, creator__in=users).exclude(id__in=self.get_reported_posts(self_user))

    def get_post_detail(self, post_id):
        return Post.objects.filter(is_valid=True, id=post_id).first()

    def get_post_by_category(self, category_id, self_user):
        if category_id:
            category_ids = category_id.split(',')
        else:
            selected_categories = SelectedCategories.objects.filter(user__id=self_user.id).first()
            category_ids = selected_categories.categories.all().values_list('id', flat=True)
        posts = Post.objects.filter(is_valid=True, category__id__in=category_ids).exclude(
            id__in=self.get_reported_posts(self_user))
        return posts.exclude(creator__id__in=UserManagement().get_user_from_blocked_list(self_user)).order_by('-id')

    def search_posts(self, data, self_user):
        return Post.objects.filter(
            (Q(title__icontains=data) | Q(description__icontains=data) | (Q(keywords__icontains=data))),
            is_valid=True).exclude(id__in=self.get_reported_posts(self_user)).distinct().order_by('-id')

    def get_postlike_by_user(self, post_id, user_id):
        return PostLike.objects.filter(user_liked__id=user_id, post__id=post_id).first()

    def get_post_rate_by_user(self, user_id, post_id):
        return PostRating.objects.filter(user_rated__id=user_id, post__id=post_id).first()

    def get_comment_by_id(self, id):
        return PostComment.objects.filter(id=id).first()

    def get_rate_by_id_user(self, id, user_id):
        return CommentRating.objects.filter(comment__id=id, user_rated__id=user_id).first()

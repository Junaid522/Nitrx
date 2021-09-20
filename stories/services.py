from datetime import datetime

from accounts.services import UserManagement
from stories.models import Story, StoryView, StoryRating


class StoryManagement(object):

    def get_story_by_id(self, id):
        return Story.objects.filter(id=id).first()

    def get_self_story_by_id(self, id, user):
        return Story.objects.filter(id=id, user=user).first()

    def get_story_viewers_by_story_id(self, id):
        return StoryView.objects.filter(story__id=id, is_valid=True).values_list('user__id', flat=True).order_by('-id')

    def get_all_stories_by_user(self, user):
        return Story.objects.filter(user=user, is_valid=True)

    def get_story_viewers(self, story):
        return StoryView.objects.filter(story=story)

    def get_stories_of_following_users(self, user):
        blocked_users = UserManagement().get_user_from_blocked_list(user)
        following_users = UserManagement().get_followings_users(user).exclude(follow__id__in=blocked_users)
        return Story.objects.filter(user__in=following_users, is_valid=True, expire_at__gte=datetime.today()).order_by(
            '-id')

    def get_stories_by_user_group(self, user_ids):
        return Story.objects.filter(user__id__in=user_ids, is_valid=True, expire_at__gte=datetime.today()).order_by(
            '-id').group_by('user').distinct().values_list('user', flat=True)

    def get_story_rate_by_id(self, id, user_id):
        return StoryRating.objects.filter(story__id=id, user_rated__id=user_id).first()

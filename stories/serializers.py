from datetime import datetime

from django.template.loader import render_to_string
from rest_framework import serializers

from accounts.models import User
from accounts.serializers import UserSerializer
from common.commmon_services import convert_time_mhr, convert_time
from stories.models import Story, StoryView, StoryRating
from stories.services import StoryManagement


class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        exclude = ('is_valid', 'expire_at',)


class StoryViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoryView
        exclude = ('is_valid',)

    def create(self, data):
        return StoryView.objects.update_or_create(story=data['story'], user=data['user'])


class StoryDetailSerializer(serializers.ModelSerializer):
    viewers = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    rates = serializers.SerializerMethodField()
    rated = serializers.SerializerMethodField()
    finish = serializers.SerializerMethodField()

    class Meta:
        model = Story
        fields = '__all__'

    def get_viewers(self, obj):
        users = StoryManagement().get_story_viewers_by_story_id(obj.id)
        return UserSerializer(User.objects.filter(id__in=users), many=True).data

    def get_created_at(self, obj):
        return convert_time_mhr(obj.created_at)

    def get_rates(self, obj):
        return StoryRateSerializer(StoryRating.objects.filter(is_valid=True, story=obj), many=True).data

    def get_rated(self, obj):
        if self.context.get('user_id'):
            is_rated = StoryRating.objects.filter(is_valid=True, story=obj,
                                                  user_rated__id=self.context.get('user_id')).first()
            if is_rated:
                return True
        return False

    def get_finish(self, obj):
        return 0


class StoryDetailByUserSerializer(serializers.ModelSerializer):
    stories = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'stories', 'image_url')

    def get_stories(self, obj):
        return StoryDetailSerializer(
            Story.objects.filter(user__id=obj.id, is_valid=True, expire_at__gte=datetime.today()).order_by(
                '-id'), context={'user_id': self.context.get('user_id')}, many=True).data


class StoryRateSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()
    user_detail = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()

    class Meta:
        model = StoryRating
        exclude = ('is_valid', 'updated_at',)

    def get_profile_image(self, obj):
        return obj.user_rated.image_url

    def get_content(self, obj):
        return render_to_string('story_rate.html', {'instance': obj})

    def get_user_detail(self, obj):
        return UserSerializer(User.objects.filter(id=obj.user_rated.id).first()).data

    def get_created_at(self, obj):
        return convert_time(obj.created_at)

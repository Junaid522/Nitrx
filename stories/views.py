import datetime as deltadays

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED
from rest_framework.views import APIView

from RestProject.constants import (STORY_CREATED_SUCCESS, STORY_VIEWED_SUCCESS, STORY_DELETED_SUCCESS,
                                   STORY_DELETED_ERROR, STORY_RATED_SUCCESS, STORY_RATED_ERROR)
from accounts.services import UserManagement
from notifications.models import Notification
from notifications.services import Notifications
from stories.serializers import (StorySerializer, StoryViewSerializer, StoryDetailSerializer,
                                 StoryDetailByUserSerializer, StoryRateSerializer)
from stories.services import StoryManagement


class StoryCreateView(APIView):
    serializer_class = StorySerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, format='json'):
        dict = request.data.copy()
        dict['user'] = self.request.user.id
        media_list = request.data.get('media_list')
        for media in media_list:
            dict['url'] = media.get('url')
            dict['story_type'] = media.get('story_type')
            serializer = self.serializer_class(data=dict)
            if serializer.is_valid():
                story = serializer.save()
                story.expire_at = story.created_at + deltadays.timedelta(days=1)
                story.save()
        return Response({"message": STORY_CREATED_SUCCESS}, status=status.HTTP_201_CREATED)


class ViewStoryView(APIView):
    serializer_class = StoryViewSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, format='json'):
        dict = request.data.copy()
        dict['user'] = self.request.user.id
        serializer = self.serializer_class(data=dict)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": STORY_VIEWED_SUCCESS}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StoryDetailView(APIView):
    serializer_class = StoryDetailSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, format='json'):
        id = request.data.get('story_id')
        return Response(self.serializer_class(StoryManagement().get_story_by_id(id)).data, status=status.HTTP_200_OK)


class StoryDeleteView(APIView):
    serializer_class = StorySerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, format='json'):
        story = StoryManagement().get_self_story_by_id(request.data.get('story_id'), self.request.user)
        message = STORY_DELETED_ERROR
        status = HTTP_400_BAD_REQUEST
        if story and story.is_valid:
            story.is_valid = False
            story.save()
            message = STORY_DELETED_SUCCESS
            status = HTTP_200_OK
        return Response({'message': message}, status=status)


class AllStoriesView(APIView):
    serializer_class = StoryDetailByUserSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, format='json'):
        blocked_users = UserManagement().get_user_from_blocked_list(self.request.user)
        following_users = UserManagement().get_followings_users(self.request.user).exclude(follow__id__in=blocked_users)
        user_ids = [user_id for user_id in following_users]
        user_ids.append(self.request.user.id)
        user_ids = StoryManagement().get_stories_by_user_group(user_ids)
        users = UserManagement().get_users_by_user_list(user_ids)
        return Response(self.serializer_class(users, context={'user_id': request.user.id}, many=True).data,
                        status=HTTP_200_OK)


class StoryRateView(APIView):
    serializer_class = StoryRateSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, format='json'):
        dict = self.request.data.copy()
        dict['user_rated'] = self.request.user.id
        story_rate = StoryManagement().get_story_rate_by_id(request.data.get('story'), self.request.user.id)
        message = STORY_RATED_SUCCESS
        status = HTTP_201_CREATED
        if not story_rate:
            serializer = self.serializer_class(data=dict)
            if serializer.is_valid():
                story_rate = serializer.save()
                story = StoryManagement().get_story_by_id(request.data.get('story'))
                story_creator = UserManagement().get_user(story.user.id)
                Notifications().create_notification(story_creator, Notification.RATE_STORY, story_rate)
            else:
                return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
        elif request.data.get('rating') in ['1', '3', '5', '7', '10']:
            story_rate.rating = request.data.get('rating')
            story_rate.save()
        else:
            message = STORY_RATED_ERROR
            status = HTTP_400_BAD_REQUEST
        return Response({"message": message}, status=status)

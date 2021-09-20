from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED
from rest_framework.views import APIView

from RestProject.constants import (POST_CREATED_SUCCESS, POST_COMMENTED_SUCCESS, POST_RATED_SUCCESS, POST_LIKED_SUCCESS,
                                   POST_REPORT_SUCCESS, POST_REPORTED_ALREADY, POST_DELETED_SUCCESS, POST_DELETED_ERROR,
                                   POST_VIEWED_SUCCESS, POST_SEARCH_ERROR, POST_LIKED_REMOVED, POST_RATED_ERROR,
                                   POST_SAVE_SUCCESS, COMMENT_RATED_ERROR)
from accounts.services import UserManagement
from notifications.models import Notification
from notifications.services import Notifications
from posts.models import BlacklistPost, Post, PostSave
from posts.serializers import (PostSerializer, PostCommentSerializer, PostRateSerializer, PostLikeSerializer,
                               BlackListPostSerializer, PostDetailSerializer, PostViewSerializer,
                               OtherUserProfileSerializer, PostMaterialSerializer, PostSaveSerializer,
                               CommentRateSerializer)
from posts.services import PostManagement
from posts.tasks import save_impressions


class PostCreateView(APIView):
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, format='json'):
        dict = self.request.data.copy()
        dict['creator'] = self.request.user.id
        serializer = self.serializer_class(data=dict)
        if serializer.is_valid():
            post = serializer.save()
            media_list = request.data.get('media_list')
            for media in media_list:
                dict['url'] = media.get('url')
                dict['post_type'] = media.get('post_type')
                material_serializer = PostMaterialSerializer(data=dict)
                if material_serializer.is_valid():
                    post_material = material_serializer.save()
                    post.media_files.add(post_material)
            return Response({"message": POST_CREATED_SUCCESS}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDeleteView(APIView):
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated,)

    def post_exist(self, data):
        obj = Post.objects.filter(id=data.get('post'), creator=self.request.user).first()
        if obj:
            return obj
        return None

    def post(self, request, format='json'):
        post = self.post_exist(request.data)
        message = POST_DELETED_SUCCESS
        status = HTTP_200_OK
        if post:
            post.is_valid = False
            post.save()
        else:
            message = POST_DELETED_ERROR
            status = HTTP_400_BAD_REQUEST
        return Response({"message": message}, status=status)


class PostDetailView(APIView):
    serializer_class = PostDetailSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        posts = PostManagement().get_post_detail(request.data.get('post_id'))
        return Response(self.serializer_class(posts, context={'user_id': self.request.user.id}).data,
                        status=status.HTTP_200_OK)


class PostViewView(APIView):
    serializer_class = PostViewSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, format='json'):
        dict = self.request.data.copy()
        dict['user_view'] = self.request.user.id
        serializer = self.serializer_class(data=dict)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": POST_VIEWED_SUCCESS}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AllPostsView(APIView):
    serializer_class = PostDetailSerializer
    permission_classes = (IsAuthenticated,)

    def get_objects(self, ):
        posts = Post.objects.filter(creator=self.request.user, is_valid=True).order_by('-id')
        save_impressions.delay(list(posts.values_list('id', flat=True)), self.request.user.id)
        return posts

    def get(self, request, *args, **kwargs):
        posts = self.get_objects()
        return Response(self.serializer_class(posts, many=True, context={'user_id': request.user.id}).data,
                        status=status.HTTP_200_OK)


class PostCommentView(APIView):
    serializer_class = PostCommentSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, format='json'):
        dict = self.request.data.copy()
        dict['user_commented'] = self.request.user.id
        serializer = self.serializer_class(data=dict)
        if serializer.is_valid():
            post_comment = serializer.save()
            parent = request.data.get('parent')
            if parent:
                parent_comment = PostManagement().get_comment_by_id(int(parent))
                users_comment = UserManagement().get_user(parent_comment.user_commented.id)
                Notifications().create_notification(users_comment, Notification.REPLY_COMMENT, post_comment)
            mentioned_users = request.data.get('mentioned_users')
            post = PostManagement().get_post_detail(request.data.get('post'))
            post_creator = UserManagement().get_user(post.creator.id)
            if mentioned_users:
                for user_id in eval(mentioned_users):
                    user = UserManagement().get_user(int(user_id))
                    if user:
                        post_comment.mentioned_users.add(user)
                        Notifications().create_notification(user, Notification.MENTION_COMMENT, post_comment)
            if not parent and post.creator.id != self.request.user.id:
                Notifications().create_notification(post_creator, Notification.COMMENT_POST, post_comment)
            return Response({"message": POST_COMMENTED_SUCCESS}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentRateView(APIView):
    serializer_class = CommentRateSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, format='json'):
        dict = self.request.data.copy()
        dict['user_rated'] = self.request.user.id
        comment_rate = PostManagement().get_rate_by_id_user(request.data.get('comment'), self.request.user.id)
        message = POST_COMMENTED_SUCCESS
        status = HTTP_201_CREATED
        if not comment_rate:
            serializer = self.serializer_class(data=dict)
            if serializer.is_valid():
                comment_rate = serializer.save()
                comment = PostManagement().get_comment_by_id(request.data.get('comment'))
                users_comment = UserManagement().get_user(comment.user_commented.id)
                Notifications().create_notification(users_comment, Notification.RATE_COMMENT, comment_rate)
            else:
                return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
        elif request.data.get('rating') in ['1', '3', '5', '7', '10']:
            comment_rate.rating = request.data.get('rating')
            comment_rate.save()
        else:
            message = COMMENT_RATED_ERROR
            status = HTTP_400_BAD_REQUEST
        return Response({"message": message}, status=status)


class PostRateView(APIView):
    serializer_class = PostRateSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, format='json'):
        dict = self.request.data.copy()
        dict['user_rated'] = self.request.user.id
        post_rate = PostManagement().get_post_rate_by_user(self.request.user.id, request.data.get('post'))
        message = POST_RATED_SUCCESS
        status = HTTP_201_CREATED
        if not post_rate:
            serializer = self.serializer_class(data=dict)
            if serializer.is_valid():
                post_rate = serializer.save()
                post = PostManagement().get_post_detail(request.data.get('post'))
                post_creator = UserManagement().get_user(post.creator.id)
                Notifications().create_notification(post_creator, Notification.RATE_POST, post_rate)
            else:
                return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
        elif request.data.get('rating') in ['1', '3', '5', '7', '10']:
            post_rate.rating = request.data.get('rating')
            post_rate.save()
        else:
            message = POST_RATED_ERROR
            status = HTTP_400_BAD_REQUEST
        return Response({"message": message}, status=status)


class PostLikeView(APIView):
    serializer_class = PostLikeSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, format='json'):
        dict = self.request.data.copy()
        dict['user_liked'] = self.request.user.id
        post_like = PostManagement().get_postlike_by_user(request.data.get('post'), self.request.user.id)
        if not post_like:
            serializer = self.serializer_class(data=dict)
            if serializer.is_valid():
                post_like = serializer.save()
                post = PostManagement().get_post_detail(self.request.data.get('post'))
                if self.request.user.id != post.creator.id:
                    user = UserManagement().get_user(post.creator.id)
                    Notifications().create_notification(user, Notification.LIKE_POST, post_like)
                return Response({"message": POST_LIKED_SUCCESS}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            if post_like.is_valid:
                post_like.is_valid = False
                message = POST_LIKED_REMOVED
            else:
                post_like.is_valid = True
                message = POST_LIKED_SUCCESS
            post_like.save()
            return Response({"message": message}, status=status.HTTP_200_OK)


class PostReportView(APIView):
    serializer_class = BlackListPostSerializer
    permission_classes = (IsAuthenticated,)

    def is_already_reported(self, data):
        return BlacklistPost.objects.filter(id=data.get('post'), user_reported=self.request.user).first()

    def post(self, request, format='json'):
        if not self.is_already_reported(request.data):
            dict = request.data.copy()
            dict['user_reported'] = self.request.user.id
            serializer = self.serializer_class(data=dict)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": POST_REPORT_SUCCESS}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": POST_REPORTED_ALREADY}, status=status.HTTP_400_BAD_REQUEST)


class MyFollowingPostsView(APIView):
    serializer_class = PostDetailSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, format='json'):
        following_users = UserManagement().get_followings_users(self.request.user)
        posts = PostManagement().get_non_reported_posts(following_users, self.request.user)
        save_impressions.delay(list(posts.values_list('id', flat=True)), self.request.user.id)
        return Response(self.serializer_class(posts, many=True).data, status=status.HTTP_200_OK)


class PostByCategoryView(APIView):
    serializer_class = PostDetailSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, format='json'):
        posts = PostManagement().get_post_by_category(request.data.get('category_id'), self.request.user)
        save_impressions.delay(list(posts.values_list('id', flat=True)), self.request.user.id)
        return Response(self.serializer_class(posts, many=True, context={'user_id': self.request.user.id}).data,
                        status=status.HTTP_200_OK)


class SearchPostsView(APIView):
    serializer_class = PostDetailSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, format='json'):
        if request.data.get('data') and len(request.data.get('data')) > 1:
            posts = PostManagement().search_posts(request.data.get('data'), self.request.user)
            save_impressions.delay(list(posts.values_list('id', flat=True)), self.request.user.id)
            return Response(self.serializer_class(posts, many=True).data, status=status.HTTP_200_OK)
        return Response({'message': POST_SEARCH_ERROR}, status=status.HTTP_400_BAD_REQUEST)


class OtherUserPostsAndProfile(APIView):
    serializer_class = OtherUserProfileSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, format='json'):
        return Response(self.serializer_class(UserManagement().get_user(request.data.get('user_id')),
                                              context={'user_id': self.request.user.id}).data,
                        status=status.HTTP_200_OK)


class PostSaveView(APIView):
    serializer_class = PostSaveSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, format='json'):
        dict = self.request.data.copy()
        dict['user'] = self.request.user.id
        serializer = self.serializer_class(data=dict)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": POST_SAVE_SUCCESS}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AllSavedPostsView(generics.ListAPIView):
    serializer_class = PostSaveSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        filter_dict = {'user': self.request.user, 'is_valid': True}
        saved_posts = PostSave.objects.filter(**filter_dict)
        return saved_posts


class TrendingPostsView(APIView):
    serializer_class = PostDetailSerializer
    permission_classes = (AllowAny,)

    def get_objects(self, ):
        posts_ids = []
        posts = Post.objects.filter(is_valid=True).order_by('-id')
        save_impressions.delay(list(posts.values_list('id', flat=True)), self.request.user.id)
        for post in posts:
            if post.media_files.all().count() < 3:
                posts_ids.append(post.id)
        return posts.exclude(id__in=posts_ids)

    def get(self, request, *args, **kwargs):
        posts = self.get_objects()
        return Response(self.serializer_class(posts, many=True).data, status=status.HTTP_200_OK)

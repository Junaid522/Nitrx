import urllib.parse

from django.db.models import Avg, Sum
from django.template.loader import render_to_string
from rest_framework import serializers

from accounts.models import User, FollowUser
from accounts.serializers import UserSerializer, FollowUserSerializer, FollowingUserSerializer
from accounts.services import UserManagement
from common.commmon_services import convert_time
from common.qrcode_generator import Qrcode
from notifications.models import Notification
from posts.models import (Post, PostComment, PostRating, PostLike, BlacklistPost, PostView, PostMaterial, PostSave,
                          CommentRating)


class PathFileField(serializers.FileField):
    # TODO: Make django/nginx respect HOST header and get rid of this class
    def to_representation(self, value):
        if not value:
            return None

        if not getattr(value, 'url', None):
            # If the file has not been saved it may not have a URL.
            return None

        return urllib.parse.unquote(value.url)


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        exclude = ('is_valid', 'media_files',)

    # def to_internal_value(self, data):
    #     image = data['image']
    #     format, imgstr = image.split(';base64,')
    #     ext = format.split('/')[-1]
    #     data['image'] = ContentFile(base64.b64decode(imgstr),
    #                                 name='{}.{}'.format(''.join(random.choices(string.ascii_uppercase +
    #                                                                            string.digits, k=6)), ext))
    #     return super().to_internal_value(data)
    def create(self, validated_data):
        post = Post.objects.create(**validated_data)
        post.save()
        return Qrcode().save_post_qrcode(post)


class PostMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostMaterial
        exclude = ('is_valid',)


class PostViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostView
        exclude = ('is_valid',)

    def create(self, data):
        return PostView.objects.update_or_create(post=data['post'], user_view=data['user_view'])


class PostDetailSerializer(serializers.ModelSerializer):
    comments = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    rates = serializers.SerializerMethodField()
    views = serializers.SerializerMethodField()
    materials = serializers.SerializerMethodField()
    creator_details = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()
    follow = serializers.SerializerMethodField()
    rated = serializers.SerializerMethodField()
    rated_value = serializers.SerializerMethodField()
    is_post_saved = serializers.SerializerMethodField()
    comments_rating_average = serializers.SerializerMethodField()
    rating_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        exclude = ('is_valid',)

    def get_rating_count(self, obj):
        post_rating = PostRating.objects.filter(post=obj)
        if post_rating:
            average = post_rating.aggregate(Sum('rating'))
            if average.get('rating__sum'):
                return average.get('rating__sum')
        return None

    def get_comments(self, obj):
        if self.context.get('user_id'):
            return PostCommentSerializer(PostComment.objects.filter(is_valid=True, post=obj, parent__isnull=True),
                                         context={'user_id': self.context.get('user_id')}, many=True).data
        return PostCommentSerializer(PostComment.objects.filter(is_valid=True, post=obj), many=True).data

    def get_comments_rating_average(self, obj):
        comment_rating = CommentRating.objects.filter(comment__post=obj)
        if comment_rating:
            average = comment_rating.aggregate(Avg('rating'))
            if average.get('rating__avg'):
                return average.get('rating__avg')
        return None

    def get_likes(self, obj):
        return PostLikeSerializer(PostLike.objects.filter(is_valid=True, post=obj), many=True).data

    def get_rates(self, obj):
        return PostRateSerializer(PostRating.objects.filter(is_valid=True, post=obj), many=True).data

    def get_views(self, obj):
        return PostViewSerializer(PostView.objects.filter(is_valid=True, post=obj), many=True).data

    def get_materials(self, obj):
        return PostMaterialSerializer(obj.media_files.all(), many=True).data

    def get_creator_details(self, obj):
        return UserSerializer(User.objects.filter(id=obj.creator.id).first()).data

    def get_liked(self, obj):
        if self.context.get('user_id'):
            is_liked = PostLike.objects.filter(is_valid=True, post=obj,
                                               user_liked__id=self.context.get('user_id')).first()
            if is_liked:
                return True
        return False

    def get_rated(self, obj):
        if self.context.get('user_id'):
            is_rated = PostRating.objects.filter(is_valid=True, post=obj,
                                                 user_rated__id=self.context.get('user_id')).first()
            if is_rated:
                return True
        return False

    def get_rated_value(self, obj):
        if self.context.get('user_id'):
            is_rated = PostRating.objects.filter(is_valid=True, post=obj,
                                                 user_rated__id=self.context.get('user_id')).first()
            if is_rated:
                return is_rated.rating
        return 0

    def get_follow(self, obj):
        if self.context.get('user_id'):
            is_followed = FollowUser.objects.filter(is_valid=True, user__id=self.context.get('user_id'),
                                                    follow__id=obj.creator.id).first()
            if is_followed:
                return True
        return False

    def get_is_post_saved(self, obj):
        if self.context.get('user_id'):
            is_saved = PostSave.objects.filter(is_valid=True, user__id=self.context.get('user_id'),
                                               post__id=obj.id).first()
            if is_saved:
                return True
        return False


class OtherUserProfileSerializer(serializers.ModelSerializer):
    posts = serializers.SerializerMethodField()
    followings = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()
    follow = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'image_url', 'bio', 'gender', 'phone_number',
                  'date_of_birth', 'country', 'search_privacy', 'posts', 'followings', 'followers', 'follow',
                  'profile_qr')

    def get_posts(self, obj):
        return PostDetailSerializer(Post.objects.filter(is_valid=True, creator__id=obj.id), many=True).data

    def get_followings(self, obj):
        if self.context.get('user_id'):
            return FollowingUserSerializer((UserManagement().get_followings(obj)),
                                           context={'user_id': self.context.get('user_id')}, many=True).data
        return FollowingUserSerializer((UserManagement().get_followings(obj)), many=True).data

    def get_followers(self, obj):
        if self.context.get('user_id'):
            return FollowUserSerializer(UserManagement().get_followers(obj),
                                        context={'user_id': self.context.get('user_id')}, many=True).data
        return FollowUserSerializer(UserManagement().get_followers(obj), many=True).data

    def get_follow(self, obj):
        if self.context.get('user_id'):
            is_followed = FollowUser.objects.filter(is_valid=True, user__id=self.context.get('user_id'),
                                                    follow__id=obj.id).first()
            if is_followed:
                return True
        return False


class PostCommentSerializer(serializers.ModelSerializer):
    content = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()
    user_detail = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    child_comments = serializers.SerializerMethodField()
    rates = serializers.SerializerMethodField()
    rated = serializers.SerializerMethodField()
    rating_count = serializers.SerializerMethodField()

    class Meta:
        model = PostComment
        fields = (
            'id', 'post', 'user_commented', 'comment', 'content', 'profile_image', 'user_detail', 'created_at',
            'child_comments', 'rates', 'rated', 'rating_count', 'parent')

    def get_rated(self, obj):
        if self.context.get('user_id'):
            is_rated = CommentRating.objects.filter(is_valid=True, comment=obj,
                                                    user_rated__id=self.context.get('user_id')).first()
            if is_rated:
                return True
        return False

    def get_rates(self, obj):
        return CommentRateSerializer(CommentRating.objects.filter(is_valid=True, comment=obj), many=True).data

    def get_rating_count(self, obj):
        commment_rating = CommentRating.objects.filter(is_valid=True, comment=obj)
        if commment_rating:
            average = commment_rating.aggregate(Sum('rating'))
            if average.get('rating__sum'):
                return average.get('rating__sum')
        return None

    def get_content(self, obj):
        type = self.context.get('type')
        if type:
            if type == Notification.REPLY_COMMENT:
                return render_to_string('post_comment_reply.html', {'instance': obj})
            elif type == Notification.MENTION_COMMENT:
                return render_to_string('post_comment_mention.html', {'instance': obj})
        return render_to_string('post_comment.html', {'instance': obj})

    def get_child_comments(self, obj):
        if self.context.get('user_id'):
            return PostCommentChildSerializer(PostComment.objects.filter(parent=obj),
                                              context={'user_id': self.context.get('user_id')},
                                              many=True).data
        return PostCommentChildSerializer(PostComment.objects.filter(parent=obj), many=True).data

    def get_profile_image(self, obj):
        return obj.user_commented.image_url

    def get_user_detail(self, obj):
        return UserSerializer(User.objects.filter(id=obj.user_commented.id).first()).data

    def get_created_at(self, obj):
        return convert_time(obj.created_at)


class PostCommentChildSerializer(serializers.ModelSerializer):
    content = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()
    user_detail = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    rates = serializers.SerializerMethodField()
    rated = serializers.SerializerMethodField()
    rating_count = serializers.SerializerMethodField()

    class Meta:
        model = PostComment
        fields = (
            'id', 'post', 'user_commented', 'comment', 'content', 'profile_image', 'user_detail', 'created_at', 'rates',
            'rated', 'rating_count')

    def get_rating_count(self, obj):
        commment_rating = CommentRating.objects.filter(is_valid=True, comment=obj)
        if commment_rating:
            average = commment_rating.aggregate(Sum('rating'))
            if average.get('rating__sum'):
                return average.get('rating__sum')
        return None

    def get_content(self, obj):
        return render_to_string('post_comment.html', {'instance': obj})

    def get_profile_image(self, obj):
        return obj.user_commented.image_url

    def get_user_detail(self, obj):
        return UserSerializer(User.objects.filter(id=obj.user_commented.id).first()).data

    def get_created_at(self, obj):
        return convert_time(obj.created_at)

    def get_rated(self, obj):
        if self.context.get('user_id'):
            is_rated = CommentRating.objects.filter(is_valid=True, comment=obj,
                                                    user_rated__id=self.context.get('user_id')).first()
            if is_rated:
                return True
        return False

    def get_rates(self, obj):
        return CommentRateSerializer(CommentRating.objects.filter(is_valid=True, comment=obj), many=True).data


class PostRateSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()
    user_detail = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()

    class Meta:
        model = PostRating
        exclude = ('is_valid', 'updated_at',)

    def get_profile_image(self, obj):
        return obj.user_rated.image_url

    def get_content(self, obj):
        return render_to_string('post_rate.html', {'instance': obj})

    def get_user_detail(self, obj):
        return UserSerializer(User.objects.filter(id=obj.user_rated.id).first()).data

    def get_created_at(self, obj):
        return convert_time(obj.created_at)


class CommentRateSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()
    user_detail = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()
    post = serializers.SerializerMethodField()

    class Meta:
        model = CommentRating
        exclude = ('is_valid', 'updated_at',)

    def get_profile_image(self, obj):
        return obj.user_rated.image_url

    def get_post(self, obj):
        return obj.comment.post.id

    def get_content(self, obj):
        return render_to_string('comment_rate.html', {'instance': obj})

    def get_user_detail(self, obj):
        return UserSerializer(User.objects.filter(id=obj.user_rated.id).first()).data

    def get_created_at(self, obj):
        return convert_time(obj.created_at)


class PostLikeSerializer(serializers.ModelSerializer):
    content = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = PostLike
        fields = ('post', 'user_liked', 'content', 'profile_image')

    def get_content(self, obj):
        return render_to_string('post_like.html', {'instance': obj})

    def get_profile_image(self, obj):
        return obj.user_liked.image_url


class BlackListPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlacklistPost
        exclude = ('is_valid',)


class PostSaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostSave
        exclude = ('is_valid',)

    post_detail = serializers.SerializerMethodField()

    def get_post_detail(self, obj):
        return PostDetailSerializer(Post.objects.filter(id=obj.post.id).first(), context={'user_id': obj.user.id}).data

from django.template.loader import render_to_string
from django_countries.serializer_fields import CountryField
from django_countries.serializers import CountryFieldMixin
from rest_framework import serializers

from accounts.models import (User, FollowUser, ReportUser, BlockUser, AccountInformation, WebsiteVerification)
from common.qrcode_generator import Qrcode


class UserSerializer(serializers.ModelSerializer):
    follow = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'first_name', 'last_name', 'age', 'email', 'bio', 'gender', 'phone_number', 'profile_qr',
            'date_of_birth', 'country', 'search_privacy', 'follow', 'email_verified', 'otp_enabled', 'image_url')

    # def to_internal_value(self, data):
    #     if data.get('image'):
    #         image = data['image']
    #         format, imgstr = image.split(';base64,')
    #         ext = format.split('/')[-1]
    #         data['image'] = ContentFile(base64.b64decode(imgstr),
    #                                     name='{}.{}'.format(''.join(random.choices(string.ascii_uppercase +
    #                                                                                string.digits, k=6)), ext))
    #     return super().to_internal_value(data)

    def get_follow(self, obj):
        if self.context.get('user_id'):
            is_followed = FollowUser.objects.filter(is_valid=True, user__id=self.context.get('user_id'),
                                                    follow__id=obj.id).first()
            if is_followed:
                return True
        return False

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.save()
        return Qrcode().save_user_qrcode(user)


class AccountInformationSerializer(CountryFieldMixin, serializers.ModelSerializer):
    country = CountryField(country_dict=True)
    gender = serializers.SerializerMethodField()
    email_verified = serializers.SerializerMethodField()
    otp_enabled = serializers.SerializerMethodField()

    class Meta:
        model = AccountInformation
        fields = (
            'country', 'site_visit', 'partner_info', 'search_privacy', 'store_contacts', 'gender', 'email_verified',
            'otp_enabled')

    def get_gender(self, obj):
        return obj.user.gender

    def get_email_verified(self, obj):
        return obj.user.email_verified

    def get_otp_enabled(self, obj):
        return obj.user.otp_enabled


class WebsiteVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebsiteVerification
        exclude = ('is_valid',)


class FollowsUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowUser
        fields = '__all__'


class FollowUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowUser
        fields = (
            'user', 'follow', 'content', 'profile_image', 'first_name', 'last_name', 'username', 'follow', 'user_id')

    content = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    follow = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()

    def get_content(self, obj):
        return render_to_string('follow_user.html', {'instance': obj.user})

    def get_profile_image(self, obj):
        return obj.user.image_url

    def get_first_name(self, obj):
        return obj.user.first_name

    def get_last_name(self, obj):
        return obj.user.last_name

    def get_username(self, obj):
        return obj.user.username

    def get_user_id(self, obj):
        return obj.user.id

    def get_follow(self, obj):
        if self.context.get('user_id'):
            is_followed = FollowUser.objects.filter(is_valid=True, user__id=self.context.get('user_id'),
                                                    follow__id=obj.user.id).first()
            if is_followed:
                return True
        return False


class FollowingUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowUser
        fields = (
            'user', 'follow', 'content', 'profile_image', 'first_name', 'last_name', 'username', 'user_id', 'follow')

    content = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    follow = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()

    def get_content(self, obj):
        return render_to_string('follow_user.html', {'instance': obj.follow})

    def get_profile_image(self, obj):
        return obj.follow.image_url

    def get_first_name(self, obj):
        return obj.follow.first_name

    def get_last_name(self, obj):
        return obj.follow.last_name

    def get_username(self, obj):
        return obj.follow.username

    def get_user_id(self, obj):
        return obj.follow.id

    def get_follow(self, obj):
        if self.context.get('user_id'):
            is_followed = FollowUser.objects.filter(is_valid=True, user__id=self.context.get('user_id'),
                                                    follow__id=obj.follow.id).first()
            if is_followed:
                return True
        return False


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('old_password', 'new_password')


class ReportUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportUser
        fields = ('user', 'reported_user')


class BlockUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockUser
        fields = ('user', 'blocked_user')


class ReportUserListSerializer(serializers.ModelSerializer):
    reported_user = serializers.SerializerMethodField()

    class Meta:
        model = ReportUser
        fields = ('reported_user',)

    def get_reported_user(self, obj):
        return UserSerializer(obj.reported_user).data


class BlockUserListSerializer(serializers.ModelSerializer):
    blocked_user = serializers.SerializerMethodField()

    class Meta:
        model = BlockUser
        fields = ('blocked_user',)

    def get_blocked_user(self, obj):
        return UserSerializer(obj.blocked_user).data

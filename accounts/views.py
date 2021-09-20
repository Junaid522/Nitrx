from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_200_OK
from rest_framework.views import APIView

from RestProject.constants import (USER_CREATED_SUCCESS, USER_FOLLOW_SUCCESS, USER_UNFOLLOW_SUCCESS,
                                   USER_UNFOLLOW_ERROR, PASSWORD_CHANGE_SUCCESS,
                                   PASSWORD_CHANGE_ERROR, USER_REPORTED_SUCCESS,
                                   USER_REPORTED_ERROR, USER_BLOCKED_SUCCESS, USER_BLOCKED_ERROR,
                                   USER_UNBLOCKED_SUCCESS, USER_UNBLOCKED_ERROR, USER_SEARCH_ERROR,
                                   USER_DEACTIVATE_SUCCESS, USER_OTP_ENABLED, USER_OTP_DISABLED, USER_OTP_SEND,
                                   OTP_ERROR, OTP_TIMEOUT)
from accounts.models import (User, AccountInformation, WebsiteVerification, Otp)
from accounts.serializers import (UserSerializer, FollowUserSerializer, ChangePasswordSerializer, ReportUserSerializer,
                                  BlockUserSerializer, BlockUserListSerializer, ReportUserListSerializer,
                                  FollowingUserSerializer, FollowsUserSerializer, AccountInformationSerializer,
                                  WebsiteVerificationSerializer)
from accounts.services import UserManagement
from notifications.models import Notification
from notifications.services import Notifications


class UserCreate(APIView):
    serializer_class = UserSerializer
    permission_classes = ()
    authentication_classes = ()

    def post(self, request, format='json'):
        dict = request.data.copy()
        dict['username'] = (request.data.get('username')).lower()
        dict['email'] = (request.data.get('email')).lower()
        dict['age'] = (request.data.get('age'))
        serializer = self.serializer_class(data=dict)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(request.data.get('password'))
            user.is_active = True
            user.save()
            if user:
                UserManagement().send_otp_email(user.id)
                return Response({"message": USER_CREATED_SUCCESS}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserExistsView(APIView):
    serializer_class = UserSerializer
    permission_classes = ()
    authentication_classes = ()

    def post(self, request, format='json'):
        message = ""
        user_exists = False
        if request.data.get('username'):
            username = (request.data.get('username')).lower()
            user = User.objects.filter(username=username).first()
            if user:
                user_exists = True
                message = "Username not available Try another"
        elif request.data.get('email'):
            email = (request.data.get('email')).lower()
            user = User.objects.filter(email=email).first()
            if user:
                user_exists = True
                message = "Email is already registered please Try another."
        return Response({"message": message, 'user_exists': user_exists}, status=status.HTTP_200_OK)


class UserProfileView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    model_class = User

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    def get_object(self):
        return self.request.user

    def get(self, request):
        serializer = self.serializer_class(self.request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AccountInformationView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AccountInformationSerializer
    model_class = AccountInformation

    def get_queryset(self):
        return AccountInformation.objects.filter(user__id=self.request.user.id)

    def get_object(self):
        return AccountInformation.objects.filter(user__id=self.request.user.id).first()

    def get(self, request):
        serializer = self.serializer_class(UserManagement().get_account_info_by_user(self.request.user))
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        dict = request.data.copy()
        dict['user'] = self.request.user.id
        serializer = self.get_serializer(instance, data=dict, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        UserManagement().update_user_gender(self.request.user.id, self.request.data.get('gender'))
        return Response(serializer.data)


class WebsiteVerificationView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WebsiteVerificationSerializer
    model_class = WebsiteVerification

    def get_queryset(self):
        return WebsiteVerification.objects.filter(user__id=self.request.user.id)

    def get_object(self):
        return WebsiteVerification.objects.filter(user__id=self.request.user.id).first()

    def get(self, request):
        serializer = self.serializer_class(UserManagement().get_webiste_by_user(self.request.user))
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        dict = request.data.copy()
        dict['user'] = self.request.user.id
        serializer = self.get_serializer(instance, data=dict, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class ChangePasswordView(UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        return self.request.user

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)
        message = PASSWORD_CHANGE_SUCCESS
        status = HTTP_201_CREATED
        if serializer.is_valid():
            if not self.object.check_password(serializer.data.get("old_password")):
                status = HTTP_400_BAD_REQUEST
                message = PASSWORD_CHANGE_ERROR
            else:
                self.object.set_password(serializer.data.get("new_password"))
                self.object.save()
        else:
            message = serializer.errors
            status = HTTP_400_BAD_REQUEST
        return Response({'message': message}, status=status)


class UserReportView(APIView):
    serializer_class = ReportUserSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, format='json'):
        message = USER_REPORTED_SUCCESS
        status = HTTP_201_CREATED
        if not UserManagement().get_user_reported(request.data, self.request.user):
            dict = request.data.copy()
            dict['user'] = self.request.user.id
            serializer = self.serializer_class(data=dict)
            if serializer.is_valid():
                serializer.save()
            else:
                message = serializer.errors
                status = HTTP_400_BAD_REQUEST
        else:
            message = USER_REPORTED_ERROR
            status = HTTP_400_BAD_REQUEST
        return Response({"message": message}, status=status)


class UserBlockView(APIView):
    serializer_class = BlockUserSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, format='json'):
        message = USER_BLOCKED_SUCCESS
        status = HTTP_201_CREATED
        block_user = UserManagement().get_blockUser(request.data, self.request.user)
        if not block_user:
            dict = request.data.copy()
            dict['user'] = self.request.user.id
            dict['is_valid'] = True
            serializer = self.serializer_class(data=dict)
            if serializer.is_valid():
                serializer.save()
            else:
                message = serializer.errors
                status = HTTP_400_BAD_REQUEST
        else:
            if block_user.is_valid:
                message = USER_BLOCKED_ERROR
                status = HTTP_400_BAD_REQUEST
            else:
                block_user.is_valid = True
                block_user.save()
        return Response({"message": message}, status=status)


class UserUnBlockView(APIView):
    serializer_class = BlockUserSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        status = HTTP_400_BAD_REQUEST
        message = USER_UNBLOCKED_ERROR
        block_user = UserManagement().get_blockUser(request.data, self.request.user)
        if block_user and block_user.is_valid:
            block_user.is_valid = False
            block_user.save()
            message = USER_UNBLOCKED_SUCCESS
            status = HTTP_201_CREATED
        return Response({'message': message}, status=status)


class UserFollowView(APIView):
    serializer_class = FollowsUserSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, format='json'):
        following_user = UserManagement().get_user_follow(request.data, self.request.user)
        user = UserManagement().get_user(request.data.get('follow'))
        status = HTTP_201_CREATED
        message = USER_FOLLOW_SUCCESS
        if not following_user:
            dict = request.data.copy()
            dict['user'] = self.request.user.id
            serializer = self.serializer_class(data=dict)
            if serializer.is_valid():
                follow_user = serializer.save()
                Notifications().create_notification(user, Notification.FOLLOWING, follow_user)
            else:
                message = serializer.errors
                status = HTTP_400_BAD_REQUEST
        else:
            if following_user.is_valid:
                following_user.is_valid = False
                message = USER_UNFOLLOW_SUCCESS
                notification = Notifications().get_notification(user, Notification.FOLLOWING, following_user.id)
                if notification:
                    notification.created_at = timezone.now()
                    notification.save()
                else:
                    Notifications().create_notification(user, Notification.FOLLOWING, following_user)
            else:
                following_user.is_valid = True
                Notifications().create_notification(user, Notification.FOLLOWING, following_user)
            following_user.save()
            status = HTTP_200_OK
        return Response({"message": message}, status=status)


class UserUnFollowView(APIView):
    serializer_class = FollowUserSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, format='json'):
        following_user = UserManagement().get_user_follow(request.data, self.request.user)
        message = USER_UNFOLLOW_ERROR
        status = HTTP_400_BAD_REQUEST
        if following_user:
            if following_user.is_valid:
                following_user.is_valid = False
                following_user.save()
                message = USER_UNFOLLOW_SUCCESS
                status = HTTP_201_CREATED
        return Response({"message": message}, status=status)


class FollowingUsersView(APIView):
    serializer_class = FollowUserSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        data = {'following': FollowingUserSerializer(UserManagement().get_followings(self.request.user),
                                                     context={'user_id': self.request.user.id}, many=True).data,
                'followers': self.serializer_class(UserManagement().get_followers(self.request.user),
                                                   context={'user_id': self.request.user.id}, many=True).data}
        return Response(data, status=status.HTTP_200_OK)


class BlockedUsersListView(APIView):
    serializer_class = BlockUserListSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        data = self.serializer_class(UserManagement().get_user_blocked_list(self.request.user), many=True).data
        return Response(data, status=status.HTTP_200_OK)


class ReportUsersListView(APIView):
    serializer_class = ReportUserListSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        data = self.serializer_class(UserManagement().get_user_reported_list(self.request.user), many=True).data
        return Response(data, status=status.HTTP_200_OK)


class SearchUsersListView(APIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if request.data.get('username') and len(request.data.get('username')) > 2:
            data = self.serializer_class(
                UserManagement().search_users_by_username(request.data.get('username'), self.request.user.id),
                context={'user_id': self.request.user.id}, many=True).data
            return Response(data, status=status.HTTP_200_OK)

        return Response({'message': USER_SEARCH_ERROR}, status=status.HTTP_400_BAD_REQUEST)


class UserDeactivateView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format='json'):
        user = UserManagement().get_user(self.request.user.id)
        user.is_active = False
        user.save()
        return Response({"message": USER_DEACTIVATE_SUCCESS}, status=HTTP_200_OK)


class OtpEmailToggleView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format='json'):
        user = UserManagement().get_user(self.request.user.id)
        if user.otp_enabled:
            user.otp_enabled = False
            message = USER_OTP_DISABLED
        else:
            user.otp_enabled = True
            message = USER_OTP_ENABLED
        user.save()
        return Response({"message": message, 'data': UserSerializer(user).data}, status=HTTP_200_OK)


class OtpEmailVerifyView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format='json'):
        otp = Otp.objects.filter(user__id=self.request.user.id).first()
        if otp:
            otp.delete()
        UserManagement().send_otp_email(self.request.user.id)
        return Response({"message": USER_OTP_SEND}, status=HTTP_200_OK)

    def post(self, request, format='json'):
        message = OTP_ERROR
        now = timezone.now()
        otp = Otp.objects.filter(user__id=self.request.user.id, code=request.data.get('code')).first()
        user = UserManagement().get_user(self.request.user.id)
        if otp:
            diff = now - otp.created_at
            if diff and diff < timedelta(minutes=1):
                message = "Success"
                user.email_verified = True
                user.save()
            else:
                message = OTP_TIMEOUT
        return Response({"message": message, 'data': UserSerializer(user).data}, status=HTTP_200_OK)


class SignupOtpEmailVerifyView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format='json'):
        message = OTP_ERROR
        now = timezone.now()
        otp = Otp.objects.filter(user__email=request.data.get('user_email'), code=request.data.get('code')).first()
        user = UserManagement().get_user_by_email(request.data.get('user_email'))
        if otp:
            diff = now - otp.created_at
            if diff and diff < timedelta(minutes=1):
                message = "Success"
                user.email_verified = True
                user.save()
            else:
                message = OTP_TIMEOUT
        return Response({"message": message}, status=HTTP_200_OK)

import string
from random import choice

from RestProject import settings
from accounts.models import FollowUser, BlockUser, ReportUser, User, AccountInformation, WebsiteVerification, Otp
from accounts.serializers import UserSerializer
from common.email_services import Email


class UserManagement(object):

    def get_user_by_email(self, email):
        return User.objects.filter(email=email).first()

    def get_all_active_users(self):
        return User.objects.filter(is_active=True, is_valid=True, is_superuser=False)

    def get_user(self, id):
        return User.objects.filter(id=id).first()

    def get_users_by_user_list(self, user_ids):
        return User.objects.filter(id__in=user_ids)

    def get_followings_users(self, user):
        return FollowUser.objects.filter(user=user, is_valid=True).values_list('follow', flat=True)

    def get_followings(self, user):
        return FollowUser.objects.filter(user=user, is_valid=True)

    def get_followers(self, user):
        return FollowUser.objects.filter(follow=user, is_valid=True)

    def get_blockUser(self, data, user):
        return BlockUser.objects.filter(user=user, blocked_user=data.get('blocked_user')).first()

    def get_user_follow(self, data, user):
        return FollowUser.objects.filter(user=user, follow=data.get('follow')).first()

    def get_user_reported(self, data, user):
        return ReportUser.objects.filter(user=user, reported_user=data.get('reported_user')).first()

    def get_user_reported_list(self, user):
        return ReportUser.objects.filter(user=user, is_valid=True)

    def get_user_blocked_list(self, user):
        return BlockUser.objects.filter(user=user, is_valid=True)

    def get_user_from_blocked_list(self, user):
        return BlockUser.objects.filter(user=user, is_valid=True).values_list('blocked_user__id', flat=True)

    def search_users_by_username(self, username, current_user):
        return User.objects.filter(username__icontains=username, is_valid=True).order_by('-id').exclude(
            id=current_user).exclude(is_superuser=True).exclude(id__in=self.get_user_from_blocked_list(current_user))

    def get_account_info_by_user(self, user):
        account_info = AccountInformation.objects.filter(user__id=user.id).first()
        if not account_info:
            user = self.get_user(user.id)
            account_info = AccountInformation(user=user)
            account_info.save()
        return account_info

    def get_webiste_by_user(self, user):
        return WebsiteVerification.objects.filter(user__id=user.id).first()

    def update_user_gender(self, user, gender):
        user = self.get_user(user)
        if gender == User.MALE:
            user.gender = User.MALE
        elif gender == User.FEMALE:
            user.gender = User.FEMALE
        elif gender == User.OTHER:
            user.gender = User.OTHER
        user.save()

    def send_otp_email(self, user_id):
        user = self.get_user(user_id)
        chars = string.digits
        code = ''.join(choice(chars) for _ in range(4))
        otp = Otp.objects.create(user=user, code=code)
        otp.save()
        Email().send_otp_email(user, otp.code)


from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from django.template.loader import render_to_string

from django_rest_passwordreset.signals import reset_password_token_created


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    """
    Handles password reset tokens
    When a token is created, an e-mail needs to be sent to the user
    :param sender: View Class that sent the signal
    :param instance: View Instance that sent the signal
    :param reset_password_token: Token Model Object
    :param args:
    :param kwargs:
    :return:
    """
    # send an e-mail to the user
    context = {
        'current_user': reset_password_token.user,
        'username': reset_password_token.user.username,
        'email': reset_password_token.user.email,
        # 'reset_password_url': "{}?token={}".format('https://nitrx.com/update_password', reset_password_token.key)
        'reset_password_url': "{}?token={}".format('http://localhost:3000/update_password', reset_password_token.key)
    }

    # render email text
    email_html_message = render_to_string('email/user_reset_password.html', context)
    email_plaintext_message = render_to_string('email/user_reset_password.txt', context)

    msg = EmailMultiAlternatives(
        # title:
        "Password Reset for {title}".format(title="Nitrx"),
        # message:
        email_plaintext_message,
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [reset_password_token.user.email]
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()


def jwt_response_payload_handler(token, user=None, request=None):
    if user.otp_enabled:
        UserManagement().send_otp_email(user.id)
    return {
        'token': token,
        'user': UserSerializer(user, context={'request': request}).data
    }

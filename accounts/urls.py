from django.conf.urls import include, url
from django.urls import path, re_path
from drf_jwt_2fa.views import (obtain_auth_token, obtain_code_token, refresh_auth_token, verify_auth_token)
from rest_framework_jwt.views import refresh_jwt_token, verify_jwt_token, obtain_jwt_token

from . import views

urlpatterns = [
    path('api/user/register', views.UserCreate.as_view(), name='account-create'),
    path('api/user/get_user', views.UserExistsView.as_view(), name='user-exists'),
    path('api/user/profile', views.UserProfileView.as_view(), name='account-profile'),
    path('api/user/deactivate', views.UserDeactivateView.as_view(), name='account-deactivate'),
    path('api/user/information', views.AccountInformationView.as_view(), name='user-info'),
    path('api/user/webitelink', views.WebsiteVerificationView.as_view(), name='user-webiste'),
    path('api/user/opt_toggle', views.OtpEmailToggleView.as_view(), name='user-otp-email'),
    path('api/user/otp_email_verified', views.OtpEmailVerifyView.as_view(), name='user-otp-email'),
    path('api/user/change_password', views.ChangePasswordView.as_view(), name='change-password'),
    path('api/user/login', obtain_jwt_token),
    path('refresh-token', refresh_jwt_token),
    re_path(r'^api-token-refresh/', refresh_jwt_token),
    re_path(r'^api-token-verify/', verify_jwt_token),
    url(r'^api/user/password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    path('api/user/report', views.UserReportView.as_view(), name='user-report'),
    path('api/user/block', views.UserBlockView.as_view(), name='user-block'),
    path('api/user/unblock', views.UserUnBlockView.as_view(), name='user-unblock'),
    path('api/user/follow', views.UserFollowView.as_view(), name='follow-user'),
    path('api/user/unfollow', views.UserUnFollowView.as_view(), name='unfollow-user'),
    path('api/user/followings', views.FollowingUsersView.as_view(), name='following-followers-users'),
    path('api/user/blocked_list', views.BlockedUsersListView.as_view(), name='blocked-user-list'),
    path('api/user/report_list', views.ReportUsersListView.as_view(), name='report-user-list'),
    url(r'^api/user/login/2fa/get-code-token/', obtain_code_token),
    url(r'^api/user/confirmation/2fa/get-auth-token/', obtain_auth_token),
    url(r'^api/user/2fa/refresh/', refresh_auth_token),
    url(r'^api/user/2fa/verify/', verify_auth_token),
    path('api/user/search', views.SearchUsersListView.as_view(), name='search-users'),
    path('api/user/signup_otp_email_verified', views.SignupOtpEmailVerifyView.as_view(), name='signup-otp-email'),
]

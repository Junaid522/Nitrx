from django.urls import path

from . import views

urlpatterns = [
    path('', views.DashBoardView.as_view(), name='dashboard'),
    path('login/', views.dashboard_login_view, name='dashboard-login'),
    path('logout/', views.dashboard_logout_view, name='dashboard-logout'),
    path('users/', views.DashBoardUsersView.as_view(), name='dashboard-users'),
]

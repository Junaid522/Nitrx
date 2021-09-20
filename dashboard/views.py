from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from RestProject.decorators import staff_required
from accounts.models import User

from accounts.services import UserManagement
from dashboard.forms import LoginForm
from dashboard.services import DashboardService
from posts.models import Post
from posts.services import PostManagement


@method_decorator(staff_required, name='dispatch')
class DashBoardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        total_users = User.objects.filter(is_active=True, is_valid=True)
        kwargs.setdefault('view', self)
        posts = Post.objects.all()
        for post in posts:
            post.__setattr__('post_media', post.media_files.first().url)
            post.__setattr__('impressions', post.postimpressions_set.count)
            post.__setattr__('total_audience', post.postlike_set.count() + post.postrating_set.count() +
                             post.postview_set.count())
            post.__setattr__('engaged_audience', post.postlike_set.count() + post.postrating_set.count() +
                             post.postview_set.count())
        kwargs['posts'] = posts
        kwargs['total_users'] = total_users
        kwargs['active_users'] = DashboardService().get_logged_in_users()
        return kwargs


@method_decorator(staff_required, name='dispatch')
class DashBoardUsersView(LoginRequiredMixin, TemplateView):
    template_name = 'users.html'

    def get_context_data(self, **kwargs):
        user_posts = []
        total_users = UserManagement().get_all_active_users()
        for user in total_users:
            user_posts.append(PostManagement().get_user_posts(user).count())
        kwargs.setdefault('view', self)
        kwargs['total_users'] = zip(total_users, user_posts)
        return kwargs


def dashboard_login_view(request):
    form = LoginForm(request.POST or None)

    msg = None

    if request.user and request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None and user.is_superuser:
                login(request, user)
                return redirect("dashboard")
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Invalid credentials'

    return render(request, "login.html", {"form": form, "msg": msg})


def dashboard_logout_view(request):
    logout(request)
    return redirect(reverse('dashboard-login'))

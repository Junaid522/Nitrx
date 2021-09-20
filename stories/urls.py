from django.urls import path

from . import views

urlpatterns = [
    path('api/story/create', views.StoryCreateView.as_view(), name='story-create'),
    path('api/story/view', views.ViewStoryView.as_view(), name='story-view'),
    path('api/story/details', views.StoryDetailView.as_view(), name='story-detail'),
    path('api/story/delete', views.StoryDeleteView.as_view(), name='story-delete'),
    path('api/story/all', views.AllStoriesView.as_view(), name='all-stories'),
    path('api/story/rate', views.StoryRateView.as_view(), name='story-rate'),

]

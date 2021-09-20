from django.urls import path

from . import views

urlpatterns = [
    path('api/post/trending', views.TrendingPostsView.as_view(), name='post-trending'),
    path('api/post/create', views.PostCreateView.as_view(), name='post-create'),
    path('api/post/view', views.PostViewView.as_view(), name='post-create'),
    path('api/post/delete', views.PostDeleteView.as_view(), name='post-delete'),
    path('api/post/save', views.PostSaveView.as_view(), name='post-save'),
    path('api/post/detail', views.PostDetailView.as_view(), name='post-detail'),
    path('api/post/all', views.AllPostsView.as_view(), name='post-all'),
    path('api/post/comment', views.PostCommentView.as_view(), name='post-comment'),
    path('api/post/comment/rate', views.CommentRateView.as_view(), name='rate-comment'),
    path('api/post/rate', views.PostRateView.as_view(), name='post-rate'),
    path('api/post/like', views.PostLikeView.as_view(), name='post-like'),
    path('api/post/report', views.PostReportView.as_view(), name='post-report'),
    path('api/post/by_category', views.PostByCategoryView.as_view(), name='post-by-category'),
    path('api/post/my_followings_posts', views.MyFollowingPostsView.as_view(), name='post-report'),
    path('api/post/search', views.SearchPostsView.as_view(), name='search-posts'),
    path('api/post/all_saved', views.AllSavedPostsView.as_view(), name='saved-posts'),
    path('api/post/other_users_detail', views.OtherUserPostsAndProfile.as_view(), name='user-profile-all-details'),
]

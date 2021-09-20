from django.urls import path

from . import views

urlpatterns = [
    path('api/category/create', views.CategoryCreateView.as_view(), name='category-create'),
    path('api/category/all', views.AllCategoriesView.as_view(), name='category-all'),
    path('api/category/selection', views.SelectCategoriesView.as_view(), name='category-select'),
    path('api/category/other', views.OtherCategoriesView.as_view(), name='other-category'),
]

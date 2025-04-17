from django.urls import path

from .views import (
    UserDetailView,
    UserListView,
    UserUpdateView,
    login_view,
    logout_view,
    profile_view,
    register_view,
)

app_name = 'accounts'

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('profile/update/', UserUpdateView.as_view(), name='profile_update'),
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user_detail'),
]
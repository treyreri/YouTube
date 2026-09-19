from django.urls import path
from .views import (
    register, login_user, logout_user, home, 
    add_video, my_profile, all_videos, verify, 
    users, user_detail, follow, unfollow
)

urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('verify/', verify, name='verify'),
    path('profile/', my_profile, name='profile'),
    path('create/', add_video, name='add_video'),
    path('videos/', all_videos, name='all_videos'),
    path('users/', users, name='users'),
    path('user/<int:id>/', user_detail, name='user_detail'),
    path('follow/<int:user_id>/', follow, name='follow'),
    path('unfollow/<int:user_id>/', unfollow, name='unfollow'),
]
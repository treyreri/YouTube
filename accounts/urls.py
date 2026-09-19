from django.urls import path
from .views import *


urlpatterns = [
    path('register',register,name='register'),
    path('login',login_user,name='login'),
    path('logout',logout_user,name='logout'),
    path('home',home,name='home'),
    path('create',add_post,name='add'),
    path('profile',my_profile,name='profile'),
    path('posts',all_posts,name='all'),
    path('verify',verify,name='verify'),
    path('users',users,name='users'),
    path('user/<int:id>',user_detail,name='user'),
    path('follow/<int:user_id>',folllow,name='follow'),
    path('unfollow/<int:user_id>',unfollow,name='unfollow'),
]

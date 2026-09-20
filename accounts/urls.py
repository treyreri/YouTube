from django.urls import path
from . import views


urlpatterns = [

    path( 'register/', views.register,  name='register' ),

    path( 'verify/', views.verify, name='verify'  ),

    path( 'login/', views.login_user, name='login' ),

    path( 'logout/',  views.logout_user,  name='logout' ),
    path('channels/create/', views.create_channel, name='create_channel'),
    path('videos/upload/', views.upload_video, name='upload_video'),
]
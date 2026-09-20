from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Count, Sum, Q
import random

from .models import ( User, Profile, Channel, Video, Follow, Like, Comment )




#authentication

def register(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        bio = request.POST.get('bio')
        avatar = request.FILES.get('avatar')

        if not username:
            return render( request, 'register.html',  {'error': 'Username is required'} )

        if not email:
            return render( request, 'register.html', {'error': 'Email is required'} )

        if not password:
            return render(  request,  'register.html',  {'error': 'Password is required'} )

        if User.objects.filter(username=username).exists():
            return render( request, 'register.html',  {'error': 'Username already exists'} )

        if User.objects.filter(email=email).exists():
            return render( request, 'register.html', {'error': 'Email already exists'} )

        verification_code = str(
            random.randint(1000, 9999)
        )

        user = User.objects.create_user( username=username, email=email,
                                         password=password, verification_code=verification_code )

        Profile.objects.create( user=user, first_name=first_name, 
                               last_name=last_name, bio=bio, avatar=avatar )

        send_mail( 'Email verification code',  f'Your verification code is: {verification_code}',
            settings.EMAIL_HOST_USER, [email] )

        return redirect('verify')

    return render(request, 'register.html')


def verify(request):

    if request.method == 'POST':

        email = request.POST.get('email')
        code = request.POST.get('code')

        try:
            user = User.objects.get(email=email)

            if user.verification_code != code:
                return render(
                    request,
                    'verify.html',
                    {'error': 'Code is incorrect'} )

            user.is_verified = True
            user.save()

            return redirect('login')

        except User.DoesNotExist:

            return render(
                request,
                'verify.html',
                {'error': 'Email not found'} )

    return render(request, 'verify.html')



def login_user(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username:
            return render( request, 'login.html', {'error': 'Username is required'} )

        if not password:
            return render(
                request,
                'login.html',
                {'error': 'Password is required'}  )

        user = authenticate(
            request,
            username=username,
            password=password )

        if user is None:
            return render(
                request,
                'login.html',
                {'error': 'Username or password is incorrect'} )

        if not user.is_verified:
            return render(
                request,
                'login.html',
                {'error': 'Email is not verified'} )

        login(request, user)

        return redirect('video_list')

    return render(request, 'login.html')


def logout_user(request):

    logout(request)

    return redirect('login')


#home

def home(request):

    return render(
        request,
        'home.html' )


#channel create

@login_required
def create_channel(request):

    if not request.user.is_verified:
        return render( request, 'error.html', {'error': 'You need to verify your email first'} )

    if request.method == 'POST':

        title = request.POST.get('title')
        description = request.POST.get('description')
        avatar = request.FILES.get('avatar')

        Channel.objects.create(
            owner=request.user, title=title,
            description=description, avatar=avatar )

        return redirect('profile')

    return render(
        request,
        'channel_create.html' )


#upload video

@login_required
def upload_video(request):

    if not request.user.is_verified:
        return render(
            request,
            'error.html',
            {'error': 'You need to verify your email first'} )

    channels = Channel.objects.filter(
        owner=request.user )

    if request.method == 'POST':

        title = request.POST.get('title')
        category = request.POST.get('category')
        description = request.POST.get('description')
        video_file = request.FILES.get('video_file')
        channel_id = request.POST.get('channel')

        channel = get_object_or_404(
            Channel,
            id=channel_id,
            owner=request.user )

        Video.objects.create(
            channel=channel,
            title=title,
            category=category,
            description=description,
            video_file=video_file )

        return redirect(
            'video_detail',
            id=Video.objects.latest('id').id )

    return render(
        request,
        'video_create.html',
        {'channels': channels} )


#video list

def video_list(request):

    search = request.GET.get('search')

    videos = Video.objects.select_related('channel').all()

    if search:
        videos = videos.filter(
            Q(title__icontains=search) |
            Q(category__icontains=search) )

    return render(
        request,
        'video_list.html',
        {
            'videos': videos,
            'search': search
        } )


#video detail

def video_detail(request, id):

    video = get_object_or_404(
        Video.objects.select_related('channel'),
        id=id )

    comments = Comment.objects.filter(
        video=video,
        parent=None ).select_related( 'user' ).prefetch_related( 'replies__user' )

    likes_count = Like.objects.filter(
        video=video
    ).count()

    liked = False

    if request.user.is_authenticated:

        liked = Like.objects.filter(
            user=request.user,
            video=video
        ).exists()

    return render(
        request,
        'video_detail.html',
        {
            'video': video,
            'comments': comments,
            'likes_count': likes_count,
            'liked': liked
        }
    )


#channel detail

def channel_detail(request, id):

    channel = get_object_or_404(
        Channel.objects.select_related('owner'),
        id=id
    )

    videos = channel.videos.all()

    subscribers = Follow.objects.filter(
        channel=channel
    ).count()

    total_likes = Like.objects.filter(
        video__channel=channel
    ).count()

    followed = False

    if request.user.is_authenticated:

        followed = Follow.objects.filter(
            user=request.user,
            channel=channel
        ).exists()

    return render(
        request,
        'channel_detail.html',
        {
            'channel': channel,
            'videos': videos,
            'subscribers': subscribers,
            'total_likes': total_likes,
            'followed': followed
        }
    )


#channel videos

def channel_videos(request, id):

    channel = get_object_or_404(
        Channel,
        id=id
    )

    videos = channel.videos.select_related(
        'channel'
    ).all()

    return render(
        request,
        'channel_videos.html',
        {
            'channel': channel,
            'videos': videos
        }
    )


#user profile

def user_profile(request, id):

    user = get_object_or_404(
        User,
        id=id
    )

    profile = get_object_or_404(
        Profile,
        user=user
    )

    channels = user.channels.all()

    return render(
        request,
        'user_profile.html',
        {
            'profile': profile,
            'channels': channels
        }
    )


@login_required
def my_profile(request):

    profile = get_object_or_404(
        Profile,
        user=request.user
    )

    channels = request.user.channels.all()

    return render(
        request,
        'profile.html',
        {
            'profile': profile,
            'channels': channels
        }
    )


#search

def search(request):

    query = request.GET.get('q')

    videos = Video.objects.select_related(
        'channel'
    ).all()

    if query:

        videos = videos.filter(
            Q(title__icontains=query) |
            Q(category__icontains=query)
        )

    return render(
        request,
        'search.html',
        {
            'videos': videos,
            'query': query
        }
    )


#follow/unfollow

@login_required
def follow(request, channel_id):

    channel = get_object_or_404(
        Channel,
        id=channel_id
    )

    Follow.objects.get_or_create(
        user=request.user,
        channel=channel
    )

    return redirect(
        'channel_detail',
        id=channel.id
    )


@login_required
def unfollow(request, channel_id):

    channel = get_object_or_404(
        Channel,
        id=channel_id
    )

    Follow.objects.filter(
        user=request.user,
        channel=channel
    ).delete()

    return redirect(
        'channel_detail',
        id=channel.id
    )


#like/unlike

@login_required
def like_video(request, video_id):

    video = get_object_or_404(
        Video,
        id=video_id
    )

    Like.objects.get_or_create(
        user=request.user,
        video=video
    )

    return redirect(
        'video_detail',
        id=video.id
    )


@login_required
def unlike_video(request, video_id):

    video = get_object_or_404(
        Video,
        id=video_id
    )

    Like.objects.filter(
        user=request.user,
        video=video
    ).delete()

    return redirect(
        'video_detail',
        id=video.id
    )



#comments

@login_required
def add_comment(request, video_id):

    video = get_object_or_404(
        Video,
        id=video_id
    )

    if request.method == 'POST':

        text = request.POST.get('text')

        Comment.objects.create(
            user=request.user,
            video=video,
            text=text
        )

    return redirect(
        'video_detail',
        id=video.id
    )


@login_required
def add_reply(request, video_id, comment_id):

    video = get_object_or_404(
        Video,
        id=video_id
    )

    parent = get_object_or_404(
        Comment,
        id=comment_id,
        video=video
    )

    if request.method == 'POST':

        text = request.POST.get('text')

        Comment.objects.create(
            user=request.user,
            video=video,
            text=text,
            parent=parent
        )

    return redirect(
        'video_detail',
        id=video.id
    )
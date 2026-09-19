from django.shortcuts import render, redirect, get_object_or_404
from .models import User, Profile, Channel, Video, Follow, Like
from django.contrib.auth import authenticate, login, logout
import random
from django.core.mail import send_mail
from django.conf import settings


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        f_name = request.POST.get('f_name')
        l_name = request.POST.get('l_name')
        bio = request.POST.get('bio')
        avatar = request.FILES.get('avatar')

        if not username:
            return render(request, 'register.html', {'error': "username is required"})
        if not password:
            return render(request, 'register.html', {'error': "password is required"})

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': "username already taken"})

        ver_code = str(random.randint(1000, 9999))
        user = User.objects.create_user(username=username, password=password, email=email, verification_code=ver_code)
        
        send_mail(
            'Email verification code',
            f'Your code is: {ver_code}',
            settings.EMAIL_HOST_USER,
            [email]
        )
        Profile.objects.create(user=user, first_name=f_name, last_name=l_name, bio=bio, avatar=avatar)
        return redirect('verify')
    return render(request, 'register.html')


def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username:
            return render(request, 'login.html', {'error': "username is required"})
        if not password:
            return render(request, 'login.html', {'error': "password is required"})

        user = authenticate(request, username=username, password=password)
        
        if user is None:
            return render(request, 'login.html', {'error': "username or password incorrect"})
        
        if not user.is_verified:
            return render(request, 'login.html', {'error': "email is not verified"})

        login(request, user)
        return redirect('profile')
    return render(request, 'login.html')


def logout_user(request):
    logout(request)
    return redirect('login')


def login_required_custom(func):
    def inner(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return func(request, *args, **kwargs)
    return inner


@login_required_custom
def home(request):
    return render(request, 'home.html', {'user': request.user.username})


@login_required_custom
def add_video(request):
    """Добавление видео на канал пользователя."""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        video_file = request.FILES.get('video_file')
        
        # Берем первый канал пользователя или создаем новый по умолчанию
        channel, _ = Channel.objects.get_or_create(
            owner=request.user, 
            defaults={'name': f"Канал {request.user.username}"}
        )

        Video.objects.create(
            channel=channel,
            title=title,
            description=description,
            video_file=video_file
        )

        return redirect('profile')
    return render(request, 'create.html')


@login_required_custom
def my_profile(request):
    user = request.user
    profile = get_object_or_404(Profile, user=user)
    
    # Получаем все видео с каналов пользователя
    videos = Video.objects.filter(channel__owner=user)
    my_followings = Follow.objects.filter(follower=user).count()

    return render(request, 'profile.html', {
        'profile': profile,
        'videos': videos,
        'follows': my_followings
    })


def all_videos(request):
    videos = Video.objects.select_related('channel').all()
    return render(request, 'posts.html', {'videos': videos})


def verify(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        code = request.POST.get('code')
        try:
            user = User.objects.get(email=email)
            if user.verification_code != code:
                return render(request, 'verify.html', {'error': 'code is not correct'})
            user.is_verified = True
            user.save()
            return redirect('login')
        except User.DoesNotExist:
            return render(request, 'verify.html', {'error': 'email not found'})

    return render(request, 'verify.html')


@login_required_custom
def users(request):
    profiles = Profile.objects.select_related('user').exclude(user=request.user)
    return render(request, 'users.html', {'profiles': profiles})


@login_required_custom
def user_detail(request, id):
    target_user = get_object_or_404(User, id=id)
    profile = get_object_or_404(Profile, user=target_user)
    
    is_followed_by_me = Follow.objects.filter(follower=request.user, following=target_user).exists()
    
    return render(request, 'user.html', {
        'profile': profile,
        'followed': is_followed_by_me
    })


@login_required_custom
def follow(request, user_id):
    follower = request.user
    following = get_object_or_404(User, id=user_id)
    
    if follower != following:
        Follow.objects.get_or_create(follower=follower, following=following)
        
    return redirect('users')


@login_required_custom
def unfollow(request, user_id):
    follower = request.user
    following = get_object_or_404(User, id=user_id)

    Follow.objects.filter(follower=follower, following=following).delete()
    return redirect('users')
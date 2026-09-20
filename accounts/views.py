from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.conf import settings
import random

from .models import User, Profile


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
            return render(
                request,
                'register.html',
                {'error': 'Username is required'}
            )

        if not email:
            return render(
                request,
                'register.html',
                {'error': 'Email is required'}
            )

        if not password:
            return render(
                request,
                'register.html',
                {'error': 'Password is required'}
            )

        if User.objects.filter(username=username).exists():
            return render(
                request,
                'register.html',
                {'error': 'Username already exists'}
            )

        if User.objects.filter(email=email).exists():
            return render(
                request,
                'register.html',
                {'error': 'Email already exists'}
            )

        verification_code = str(
            random.randint(1000, 9999)
        )

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            verification_code=verification_code
        )

        Profile.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            bio=bio,
            avatar=avatar
        )

        send_mail(
            'Email verification code',
            f'Your verification code is: {verification_code}',
            settings.EMAIL_HOST_USER,
            [email]
        )

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
                    {'error': 'Code is incorrect'}
                )

            user.is_verified = True
            user.save()

            return redirect('login')

        except User.DoesNotExist:

            return render(
                request,
                'verify.html',
                {'error': 'Email not found'}
            )

    return render(request, 'verify.html')


def login_user(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username:
            return render(
                request,
                'login.html',
                {'error': 'Username is required'}
            )

        if not password:
            return render(
                request,
                'login.html',
                {'error': 'Password is required'}
            )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is None:
            return render(
                request,
                'login.html',
                {'error': 'Username or password is incorrect'}
            )

        if not user.is_verified:
            return render(
                request,
                'login.html',
                {'error': 'Email is not verified'}
            )

        login(request, user)

        return redirect('home')

    return render(request, 'login.html')


def logout_user(request):

    logout(request)

    return redirect('login')
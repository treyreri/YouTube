from django.shortcuts import render,redirect,get_object_or_404
from .models import User ,Post,Profile,Follow
from django.contrib.auth import authenticate,login,logout
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
            return render(request,'register.html',{'error':"username is requared"})
        if not password:
            return render(request,'register.html',{'error':"password is requared"})

        if User.objects.filter(username=username).exists():
            return render(request,'register.html',{'error':"username already taken"})

        ver_code = str(random.randint(1000,9999))
        user = User.objects.create_user(username=username,password=password,email=email,verification_code=ver_code)
        send_mail(
            'Email verification code',
            f'Your code is : {ver_code}',
            settings.EMAIL_HOST_USER,
            [email]
        )
        Profile.objects.create(user = user,first_name=f_name,last_name=l_name,bio=bio,avatar = avatar)
        return redirect('verify')
    return render(request,'register.html')


def login_user(request):
    if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
    
            if not username:
                return render(request,'login.html',{'error':"username is requared"})
            if not password:
                return render(request,'login.html',{'error':"password is requared"})
    
             

            user = authenticate(request,username=username,password=password)
            if user.is_verified == False:
                            return render(request,'login.html',{'error':"email is not veified"})
            if user is None:
                return render(request,'login.html',{'error':"username or password incorrect"})

            login(request,user)
            
            return redirect('profile')
    return render(request,'login.html')


def logout_user(request):
    logout(request)
    return redirect('login')

def login_requared(func):
    def inner(request,*args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return func(request,*args, **kwargs)
    return inner
            
@login_requared
def home(request):
    return render(request,'home.html',{'user':request.user.username})   

@login_requared        
def add_post(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')

        Post.objects.create(title = title,description=description,owner = request.user)

        return redirect('profile')
    return render(request,'create.html')




@login_requared
def my_profile(request):
    user = request.user
    profile  = Profile.objects.get(user = user)
    posts = Post.objects.filter(owner = user)
    my_followings = Follow.objects.filter(follower = user).count()

    return render(request,'profile.html',{'profile':profile,'posts':posts,'follows':my_followings})


def all_posts(request):
    posts = Post.objects.all()
    return render(request,'posts.html',{'posts':posts})


def verify(request):
    if request.method=='POST':
         email = request.POST.get('email')
         code = request.POST.get('code')
         print(email,code)
         try:
            user = User.objects.get(email=email)
            if user.verification_code!=code:
                    return render(request,'verify.html',{'error':'code is not correct'})
            user.is_verified = True
            user.save()
            return redirect('login')
         except:
              return render(request,'verify.html',{'error':'email not found'})
          
              
              
    return render(request,'verify.html')


@login_requared
def users(request):
    
     profiles = Profile.objects.select_related('user').exclude(user=request.user)
     
     

     return render(request,'users.html',{'profiles':profiles})

@login_requared
def user_detail(request,id):
     user = User.objects.get(id = id)
     print(user)
     profile = Profile.objects.select_related('user').get(user = user )
     print(profile)
     try:
        is_followed_by_me = Follow.objects.get(follower = request.user,following = user) 
        return render(request,'user.html',{'profile':profile,'followed':is_followed_by_me})
     except:
          is_followed_by_me = False
          return render(request,'user.html',{'profile':profile,'followed':is_followed_by_me})
     



def folllow(request,user_id):
     follower = request.user
     following = User.objects.get(id=user_id)
     if follower == following:
          return redirect('profile')
     Follow.objects.create(follower=follower,following=following)
     return redirect('users')


def unfollow(request,user_id):
     follower = request.user
     following = User.objects.get(id = user_id)

     folow = Follow.objects.get(follower=follower,following=following)
     folow.delete()

     return redirect('users')
     
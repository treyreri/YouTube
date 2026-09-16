from django.shortcuts import render,redirect
from .models import User ,Post,Profile
from django.contrib.auth import authenticate,login,logout

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
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


        user = User.objects.create_user(username=username,password=password)
        Profile.objects.create(user = user,first_name=f_name,last_name=l_name,bio=bio,avatar = avatar)
        return redirect('login')
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

    return render(request,'profile.html',{'profile':profile,'posts':posts})


def all_posts(request):
    posts = Post.objects.all()
    return render(request,'posts.html',{'posts':posts})
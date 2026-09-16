from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    username = models.CharField( max_length=100,unique=True)
    password = models.CharField( max_length=50)

    def __str__(self):
        return self.username

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField()
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    avatar = models.ImageField(  upload_to='accounts/photos')

    def __str__(self):
        return f'profile of {self.first_name} {self.last_name}'



class Post(models.Model):
    title = models.CharField( max_length=50)
    description = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
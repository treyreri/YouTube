from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=254, unique=True)

    verification_code = models.CharField(max_length=50, blank=True, null=True )

    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class Profile(models.Model):
    user = models.OneToOneField( User, on_delete=models.CASCADE )
    bio = models.TextField( blank=True )

    first_name = models.CharField( max_length=50, blank=True )

    last_name = models.CharField(max_length=50, blank=True )

    avatar = models.ImageField( upload_to='accounts/photos', blank=True, null=True )

    def __str__(self):
        return f'Profile of {self.user.username}'


class Channel(models.Model):
    owner = models.ForeignKey( User, on_delete=models.CASCADE, related_name='channels' )

    name = models.CharField( max_length=100 )

    description = models.TextField( blank=True )

    created_at = models.DateTimeField( auto_now_add=True)

    def __str__(self):
        return self.name


class Video(models.Model):
    channel = models.ForeignKey( Channel, on_delete=models.CASCADE, related_name='videos')

    title = models.CharField( max_length=150 )

    description = models.TextField( blank=True)

    video_file = models.FileField( upload_to='videos/')

    created_at = models.DateTimeField( auto_now_add=True)

    def __str__(self):
        return self.title


class Follow(models.Model):
    follower = models.ForeignKey( User, on_delete=models.CASCADE, related_name='following')

    following = models.ForeignKey( User, on_delete=models.CASCADE, related_name='followers')

    created_at = models.DateTimeField( auto_now_add=True )

    def __str__(self):
        return f'{self.follower} follows {self.following}'


class Like(models.Model):
    user = models.ForeignKey( User, on_delete=models.CASCADE, related_name='likes' )

    video = models.ForeignKey( Video, on_delete=models.CASCADE, related_name='likes')

    created_at = models.DateTimeField( auto_now_add=True)

    class Meta:
        unique_together = ('user', 'video')

    def __str__(self):
        return f'{self.user} likes {self.video}'
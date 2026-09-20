
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    username = models.CharField( max_length=100, unique=True)

    email = models.EmailField( max_length=254, unique=True )

    verification_code = models.CharField( max_length=50, blank=True, null=True)

    is_verified = models.BooleanField( default=False )

    def __str__(self):
        return self.username


class Profile(models.Model):
    user = models.OneToOneField( User, on_delete=models.CASCADE, related_name='profile')

    bio = models.TextField(blank=True)

    first_name = models.CharField( max_length=50, blank=True )

    last_name = models.CharField( max_length=50, blank=True)

    avatar = models.ImageField( upload_to='accounts/photos/', blank=True, null=True )

    def __str__(self):
        return f'Profile of {self.user.username}'


class Channel(models.Model):
    owner = models.ForeignKey( User, on_delete=models.CASCADE, related_name='channels' )

    title = models.CharField(max_length=100)

    description = models.TextField(blank=True)

    avatar = models.ImageField( upload_to='channels/avatars/', blank=True, null=True )

    created_at = models.DateTimeField( auto_now_add=True )

    def __str__(self):
        return self.title


class Video(models.Model):
    channel = models.ForeignKey( Channel,on_delete=models.CASCADE, related_name='videos' )

    title = models.CharField(max_length=150)

    category = models.CharField(max_length=100)

    description = models.TextField(blank=True)

    video_file = models.FileField( upload_to='videos/')

    created_at = models.DateTimeField( auto_now_add=True  )

    def __str__(self):
        return self.title


class Follow(models.Model):
    user = models.ForeignKey( User, on_delete=models.CASCADE,  related_name='follows' )

    channel = models.ForeignKey( Channel, on_delete=models.CASCADE, related_name='followers' )

    created_at = models.DateTimeField( auto_now_add=True )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'channel'],
                name='unique_user_channel_follow'
            )
        ]

    def __str__(self):
        return f'{self.user.username} follows {self.channel.title}'


class Like(models.Model):
    user = models.ForeignKey( User, on_delete=models.CASCADE, related_name='likes' )

    video = models.ForeignKey( Video, on_delete=models.CASCADE, related_name='likes' )

    created_at = models.DateTimeField( auto_now_add=True )

    class Meta:
        constraints = [
            models.UniqueConstraint( fields=['user', 'video'], name='unique_user_video_like' ) ]

    def __str__(self):
        return f'{self.user.username} likes {self.video.title}'


class Comment(models.Model):
    user = models.ForeignKey( User, on_delete=models.CASCADE, related_name='comments')

    video = models.ForeignKey( Video, on_delete=models.CASCADE, related_name='comments')

    text = models.TextField()

    parent = models.ForeignKey( 'self', on_delete=models.CASCADE, blank=True, null=True, related_name='replies'  )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username}: {self.text[:30]}'
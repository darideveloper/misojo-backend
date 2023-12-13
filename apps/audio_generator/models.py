from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """ User model based on AbstractUser """
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=False)
     
    USERNAME_FIELD = 'email'


class File(models.Model):
    """ Text file uploaded to convert to audio """
    
    def user_upload_to(instance, filename):
        return f"files/{instance.user.username}/{filename}"
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    path = models.FileField(upload_to=user_upload_to)
    current_page = models.IntegerField(default=1)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    
    
class Track(models.Model):
    """ Audios created from text files """
    
    def user_upload_to(instance, filename):
        return f"tracks/{instance.user.username}/{filename}"

    id = models.AutoField(primary_key=True)
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    path = models.FileField(upload_to=user_upload_to)
    page = models.IntegerField()
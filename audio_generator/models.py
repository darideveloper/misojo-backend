from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class UserManager(BaseUserManager):
    """ Custom user model manager """
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        user = self.create_user(
            email,
            password=password,
            **extra_fields
        )
        user.is_admin = True
        user.is_active = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    """ User model based on AbstractUser """
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    username = None
    
    objects = UserManager()
     
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        if self.is_admin:
            return True

    def has_module_perms(self, app_label):
        if self.is_admin:
            return True

    @property
    def is_staff(self):
        return self.is_admin
    

class File(models.Model):
    """ Text file uploaded to convert to audio """
    
    def user_upload_to(instance, filename):
        return f"files/{instance.user.username}/{filename}"
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='files')
    path = models.FileField(upload_to=user_upload_to)
    current_page = models.IntegerField(default=1)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    
    
class Track(models.Model):
    """ Audios created from text files """
    
    def user_upload_to(instance, filename):
        return f"tracks/{instance.user.username}/{filename}"

    id = models.AutoField(primary_key=True)
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='tracks')
    path = models.FileField(upload_to=user_upload_to)
    page = models.IntegerField()
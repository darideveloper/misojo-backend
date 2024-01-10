import os
import requests
from django.db import models
from django.conf import settings
from django.core.files import File as django_file
from django.template.loader import render_to_string
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.mail import EmailMultiAlternatives
from libs.audio import generate_audio
from libs.pdf import get_pdf_text
from misojo.settings import MEDIA_ROOT


class UserManager(BaseUserManager):
    """ Custom user model manager for create new users"""
    
    def create_user(self, email: str, password: str = None,
                    **extra_fields) -> object:
        """ Create new regular user and send activation email

        Args:
            email (str): user email
            password (str, optional): user password. Defaults to None.

        Returns:
            object: User object
        """
        
        # Create regular user
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        
        # Send activation email
        activation_link = f"{settings.HOST}/activate/{user.id}"
        text_content = f"Activation link: {activation_link}"
        html_template_path = "audio_generator/activate.html"
        html_content = render_to_string(html_template_path, {
            "activation_link": activation_link,
        })
        
        msg = EmailMultiAlternatives(
            "Activate your Misojo account",
            text_content,
            settings.EMAIL_HOST_USER,
            [email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        
        return user
    
    def create_superuser(self, email: str, password: str = None,
                         **extra_fields) -> object:
        """ Create new superuser
        (regular user, already activated, with admin permissions)
        
        Args:
            email (str): user email
            password (str, optional): user password. Defaults to None.
        
        Returns:
            object: User object
        """
        
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
    """ User model based on AbstractUser, for use email as username """
    
    id = models.AutoField(primary_key=True)
    email = models.EmailField(
        unique=True,
        error_messages={
            "unique": "API.REGISTER.DUPLICATED",
        }
    )
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
        """ Set all permissions to admin user """
        if self.is_admin:
            return True

    def has_module_perms(self, app_label):
        """ Set all permissions to admin user """
        if self.is_admin:
            return True

    @property
    def is_staff(self) -> bool:
        """ Get staff status of user
        
        Returns:
            bool: True if user is admin
        """
        return self.is_admin
    

class File(models.Model):
    """ Text file uploaded to convert to audio """
    
    def user_upload_to(instance, filename) -> str:
        """ Get path to save file
        
        Returns:
            str: path to save file
        """
        return f"files/{instance.user.email}/{filename}"
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='files')
    path = models.FileField(upload_to=user_upload_to)
    current_page = models.IntegerField(default=1)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    name = models.CharField(editable=False)
            
    def generate_tracks(self):
        """ Generate audios/tracks for the next 5 pages """
        
        # Get current related tracks
        tracks = self.tracks.filter(file=self)
        tracks_pages = list(map(lambda track: track.page, tracks))
        
        # Generate new required audios
        for page in range(self.current_page, self.current_page + 5):
            
            # Skip if audio its already generated
            if page in tracks_pages:
                continue
            
            # Genare and end if page not exists
            print(f"generating audio for file {self} in page {page}")
            generated = self.generate_track(page)
            if not generated:
                break
            
    def generate_track(self, page: int) -> bool:
        """ Create specific track for a single page
        
        Args:
            page (int): page number to generate audio
            
        Returns:
            bool: True if audio was generated, False otherwise
        """
        
        # Download aws files
        url = self.path.url
        if url.startswith('https://misojo.s3.amazonaws.com/'):
            response = requests.get(url)
            file_folder = os.path.join(
                MEDIA_ROOT,
                "files",
                self.user.email,
            )
            os.makedirs(file_folder, exist_ok=True)
            pdf_path = os.path.join(file_folder, self.name)
            with open(pdf_path, 'wb') as file:
                file.write(response.content)
        else:
            pdf_path = self.path.path
        
        # Get text from pdf and validate if its generated
        text, generated = get_pdf_text(pdf_path, page)
        if not generated:
            return False
        
        # Create and save track
        file_name = f"{self.name}_{page}.mp3"
        file_path = os.path.join(
            MEDIA_ROOT,
            "files",
            self.user.email,
            file_name
        )
        track_path = generate_audio(text, 'es', file_path)
        track_obj = Track.objects.create(
            file=self,
            page=page
        )
        with open(track_path, 'rb') as track_file:
            file = django_file(track_file)
            track_obj.path.save(file_name, file, save=True)
        track_obj.save()
        
        return True
            
    def save(self, *args, **kwargs):
        """ Set file base name as name """
        self.name = self.path.name.split('/')[-1]
        super().save(*args, **kwargs)
        self.generate_tracks()
    
    def __str__(self):
        return self.name
    
    
class Track(models.Model):
    """ Audios created from text files """
    
    def user_upload_to(instance, filename) -> str:
        """ Get path to save file
        
        Returns:
            str: path to save file
        """
        return f"tracks/{instance.file.user.email}/{filename}"

    id = models.AutoField(primary_key=True)
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='tracks')
    path = models.FileField(upload_to=user_upload_to)
    page = models.IntegerField()
    name = models.CharField(max_length=50, blank=True, editable=False)
    
    def __save__(self, *args, **kwargs):
        """ Set file base name as name """
        self.name = self.path.name.split('/')[-1]
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
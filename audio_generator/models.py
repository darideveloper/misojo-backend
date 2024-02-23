import os
import requests
from threading import Thread
from django.db import models
from django.conf import settings
from django.core.files import File as django_file
from django.template.loader import render_to_string
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.mail import EmailMultiAlternatives
from libs.audio import generate_audio as gtts_generate_audio
from libs.pdf import get_pdf_text, split_pdf as split_pdf_lib
from misojo.settings import MEDIA_ROOT, TEMP_FOLDER
from django.db.models.signals import post_save
from django.dispatch import receiver


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
    
    LANGS = [
        ('es', 'Spanish'),
        ('en', 'English'),
    ]
    
    def user_upload_to(instance, filename) -> str:
        """ Get path to save file
        
        Returns:
            str: path to save file
        """
        email_clean = instance.user.email.replace("@", "_").replace(".", "_")
        return f"files/{email_clean}/{filename}"
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='files')
    path = models.FileField(upload_to=user_upload_to, max_length=500)
    current_page = models.IntegerField(default=1)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    name = models.CharField(editable=False)
    pages_num = models.IntegerField(default=0)
    lang = models.CharField(max_length=2, choices=LANGS, default='en')
    
    def split_pdf(self):
        """ Split pdf file and create pages instances """
        
        # Split pdf file
        username = self.user.email
        output_path = os.path.join(TEMP_FOLDER, username, self.name)
        os.makedirs(output_path, exist_ok=True)
        self.pages_num = split_pdf_lib(self.path.url, output_path)
        
        # Save pages instances
        pdf_pages = os.listdir(output_path)
        for page_pdf in pdf_pages:
            page_path = os.path.join(output_path, page_pdf)
            page_num = int(page_pdf.split('.')[0])
            
            print(f"creating page {page_num} for file {self}")
            
            # Base instance
            page_obj = Page.objects.create(
                file=self,
                page_num=page_num,
            )
            
            # Add file
            with open(page_path, 'rb') as track_file:
                file = django_file(track_file)
                page_obj.path_pdf.save(page_pdf, file, save=True)
            page_obj.save()
            
        print(f"pages created for file {self}")
    
    def save(self, *args, **kwargs):
        """ Set file base name as name """
        
        # Remove special chars from pdf file path
        clean_chars = [
            "-",
            " ",
            "/",
            "\\",
            "?",
            "!",
            "'",
            '"',
            "(",
            ")",
        ]
                
        if not self.name:
            self.name = self.path.name.split('/')[-1]
            self.name = self.name.replace(".pdf", "").strip().lower()
            for char in clean_chars:
                self.name = self.name.replace(char, "_")
                                
        super().save(*args, **kwargs)
                 
    def __str__(self):
        return self.name
    

# Split pdf file after save
@receiver(post_save, sender=File)
def file_updated(sender, instance, created, **kwargs):
    if created:
        # Split pdf in background
        Thread(target=instance.split_pdf).start()
        

class Page(models.Model):
    """ Pages (audios and single page pdf files)  created from pdf files """
    
    def user_upload_to(instance, page_file) -> str:
        """ Get path to save file
        
        Returns:
            str: path to save file
        """
        return f"pages/{instance.file.user.email}/{instance.file.name}/{page_file}"

    id = models.AutoField(primary_key=True)
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='tracks')
    path_audio = models.FileField(upload_to=user_upload_to, max_length=500)
    path_pdf = models.FileField(upload_to=user_upload_to, max_length=500)
    page_num = models.IntegerField()
    
    def generate_audio(self):
        """ Create specific track for a single page
        """
    
        print(f"downloading pdf for file {self} in page {self.page_num}")
        
        # Download aws files
        url = self.path_pdf.url
        if url.startswith('https://misojo.s3.amazonaws.com/'):
            response = requests.get(url)
            file_folder = os.path.join(
                MEDIA_ROOT,
                "files",
                self.file.user.email,
            )
            os.makedirs(file_folder, exist_ok=True)
            pdf_path = os.path.join(file_folder, self.name)
            with open(pdf_path, 'wb') as file:
                file.write(response.content)
        else:
            pdf_path = self.path_pdf.path
        
        print(f"getting text from pdf for file {self.file} in page {self.page_num}")
        
        # Get text from pdf and validate if its generated
        text = get_pdf_text(pdf_path)
        
        # Create and save track
        print(f"creating audio for file {self.file} in page {self.page_num}")
        audio_name = f"{self.page_num}.mp3"
        file_path = os.path.join(
            TEMP_FOLDER,
            "pages",
            self.file.user.email,
            self.file.name,
            audio_name
        )
        audio_path = gtts_generate_audio(text, self.file.lang, file_path)
        with open(audio_path, 'rb') as track_file:
            file = django_file(track_file)
            self.path_audio.save(audio_name, file, save=True)
            
        print(f"audio created for file {self.file} in page {self.page_num}")
        self.save()
    
    def __str__(self):
        return f"{self.file}/{self.page_num}"
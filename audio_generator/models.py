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
    
    STATUS_CHOICES = (
        (0, 'Uploading'),
        (1, 'Splitting'),
        (2, 'Generating'),
        (3, 'Completed'),
    )
    
    def user_upload_to(instance, filename) -> str:
        """ Get path to save file
        
        Returns:
            str: path to save file
        """
        email_clean = instance.user.email.replace("@", "_").replace(".", "_")
        return f"files/{email_clean}/{filename}"
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='files')
    path = models.FileField(upload_to=user_upload_to)
    current_page = models.IntegerField(default=1)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    name = models.CharField(editable=False)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    working_processes = models.IntegerField(default=0)
    pages_num = models.IntegerField(default=0)
    
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
                  
    def generate_audio(self, page: object) -> bool:
        """ Create specific track for a single page
        
        Args:
            page (int): page number to generate audio
            
        Returns:
            bool: True if audio was generated, False otherwise
        """
    
        print(f"downloading pdf for file {self} in page {page.page_num}")
        
        # Download aws files
        url = page.path_pdf.url
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
            pdf_path = page.path_pdf.path
        
        print(f"getting text from pdf for file {self} in page {page.page_num}")
        
        # Get text from pdf and validate if its generated
        text = get_pdf_text(pdf_path)
        
        # Create and save track
        print(f"creating audio for file {self} in page {page.page_num}")
        file_name = f"{page.page_num}.mp3"
        file_path = os.path.join(
            TEMP_FOLDER,
            "pages",
            self.user.email,
            self.name,
            file_name
        )
        audio_path = gtts_generate_audio(text, 'es', file_path)
        with open(audio_path, 'rb') as track_file:
            file = django_file(track_file)
            page.path_audio.save(file_name, file, save=True)
            
        print(f"audio created for file {self} in page {page.page_num}")
        page.save()
        
        # Reduce working processes
        self.working_processes -= 1
        
        # If there are no more working processes, set status to completed
        if self.working_processes == 0:
            self.status = 3
            self.save()
            
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
            
        # Split pdf file first time and generate first audios
        if self.status == 0:
            super().save(*args, **kwargs)
            self.status = 1
            self.split_pdf()
            
        # Generate audios each update (like each time page change)
        for page in range(self.current_page, self.current_page + 5):
            
            # Validate if is required to generated an audio
            page = Page.objects.filter(file=self, page_num=page, path_audio='')
            if not page:
                continue
            page = page[0]
            
            # Increase working processes
            self.working_processes += 1
            
            # Change status to generating
            if self.status != 2:
                self.status = 2
            
            # Genare and end if page not exists
            print(f"audio required for file {self} in page {page.page_num}")
            generate_audio_thread = Thread(target=self.generate_audio, args=(page,))
            generate_audio_thread.start()
            
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    
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
    path_audio = models.FileField(upload_to=user_upload_to)
    path_pdf = models.FileField(upload_to=user_upload_to)
    page_num = models.IntegerField()
    
    def __str__(self):
        return f"{self.file}/{self.page_num}"
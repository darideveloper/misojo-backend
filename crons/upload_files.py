# Add parent folder to path
import os
import sys
import django
from time import sleep
from dotenv import load_dotenv
from django.core.files import File as django_file

# PATHS
CURRENT_FOLDER = os.path.dirname(__file__)
PARENT_FOLDER = os.path.dirname(CURRENT_FOLDER)
FILES_PARENT_FOLDER = os.path.join(CURRENT_FOLDER, "pdfs-to-upload")

# Setup parent folder
sys.path.append(PARENT_FOLDER)

# Setup django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'misojo.settings')
django.setup()

# Django imports
from audio_generator.models import File, User

# Env variables
load_dotenv()
PUBLIC_USER = os.getenv("PUBLIC_USER")

files_folders = {
    "en": os.path.join(FILES_PARENT_FOLDER, "en"),
    "es": os.path.join(FILES_PARENT_FOLDER, "es"),
}

public_user_obj = User.objects.get(email=PUBLIC_USER)

for lang, folder in files_folders.items():
    for file_name in os.listdir(folder):
        
        # Clean file name
        file_name_clean = file_name.replace(".pdf", "")
        
        # Skip file if it already exists
        if File.objects.filter(name=file_name_clean, lang=lang).exists():
            print(f"file {file_name_clean} already exists")
            continue
        
        # Base instance
        file_obj = File(
            user=public_user_obj,
            lang=lang,
            name=file_name_clean,
        )
        
        # Add file
        file_path = os.path.join(folder, file_name)
        file_name = os.path.basename(file_path)
        with open(file_path, 'rb') as track_file:
            file = django_file(track_file)
            file_obj.path.save(file_name, file, save=True)
            file_obj.save()
            
        # Wait until pages are generated
        print(f"file {file_name_clean} uploaded. Generating pages...")
        while not file_obj.pages_generated:
            sleep(2)
            
        print(f"file {file_name_clean} uploaded")
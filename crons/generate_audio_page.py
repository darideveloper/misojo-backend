
# Add parent folder to path
import os
import sys
import django

# Setup parent folder
parent_folder = os.path.dirname(os.path.dirname(__file__))
print(parent_folder)
sys.path.append(parent_folder)

# Setup django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'misojo.settings')
django.setup()

# Django imports
from audio_generator.models import Page

# Detect pages with missing audio
pages = Page.objects.filter(
    path_audio='',
).order_by('id')

print(f"Pages with missing audio: {pages.count()}")

# Generate audio for a single page
if pages:
    print(f"Generating audio for page {pages.first()}")
    page = pages.first()
    page.generate_audio()
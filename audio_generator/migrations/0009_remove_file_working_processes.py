# Generated by Django 4.2.7 on 2024-02-21 16:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('audio_generator', '0008_alter_file_path_alter_page_path_audio_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='file',
            name='working_processes',
        ),
    ]
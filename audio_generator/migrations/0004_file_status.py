# Generated by Django 4.2.7 on 2024-01-15 21:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audio_generator', '0003_page_delete_track'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='status',
            field=models.CharField(choices=[('0', 'Uploading'), ('1', 'Splitting'), ('2', 'Generating'), ('3', 'Completed')], default='0', max_length=10),
        ),
    ]
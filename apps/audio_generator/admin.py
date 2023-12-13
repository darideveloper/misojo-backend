from django.contrib import admin
from .models import File, Track


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'path', 'current_page', 'uploaded_at', 'last_modified')
    list_filter = ('user', 'uploaded_at', 'last_modified')
    search_fields = ('user', 'path', 'uploaded_at', 'last_modified')


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ('id', 'file', 'path', 'page')
    list_filter = ('file', 'page')
    search_fields = ('file', 'path', 'page')
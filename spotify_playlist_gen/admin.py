from django.contrib import admin
from .models import Song

class SongAdmin(admin.ModelAdmin):
    song_display = ('title', 'description')

# Register your models here.

admin.site.register(Song, SongAdmin)

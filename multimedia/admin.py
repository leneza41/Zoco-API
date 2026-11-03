from django.contrib import admin
from .models import Media


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'media_type', 'media_uri', 'description', 'created_at')
    list_filter = ('media_type', 'created_at')
    search_fields = ('description', 'media_uri')

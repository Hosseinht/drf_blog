from django.contrib import admin

from .models import Category, Post


class PostAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "category", "status"]
    list_display_link = ["title", "author", "category"]
    search_fields = ["author__email", "title"]
    list_filter = ["category", "author__email"]
    # readonly_fields = ['slug']


admin.site.register(Category)
admin.site.register(Post, PostAdmin)

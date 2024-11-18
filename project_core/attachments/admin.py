from django.contrib import admin
from .models import *


@admin.register(URL)
class URLAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'alternative', 'url', 'type', 'added_at')
    search_fields = ('name', 'alternative', 'url')
    list_filter = ('type', 'added_at')

@admin.register(TypeOfURL)
class TypeOfURLAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)
    search_fields = ('name',)

@admin.register(TypeOfAuthor)
class TypeOfAuthorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)
    search_fields = ('name',)

@admin.register(MetaKword)
class MetaKwordAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)
    search_fields = ('name',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'type')
    search_fields = ('name',)
    list_filter = ('type',)


@admin.register(LinkOfPosts)
class LinkOfPostsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'address', 'added_at')
    search_fields = ('name', 'address')
    list_filter = ('added_at',)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'confirm')
    search_fields = ('name',)
    list_filter = ('confirm',)


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)
    search_fields = ('name',)
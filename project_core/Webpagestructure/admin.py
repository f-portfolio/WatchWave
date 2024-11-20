from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from easy_select2 import Select2
from .models import *  # Import your models





@admin.register(SiteHeader)
class SiteHeaderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_date', 'updated_date')
    search_fields = ('name', 'alternative_logo', )
    readonly_fields = ('created_date', 'updated_date')


@admin.register(LinkSection)
class LinkSectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_date', 'updated_date')
    list_filter = ('link', )
    search_fields = ('name', 'alternative_link', 'link')
    readonly_fields = ('created_date', 'updated_date')


@admin.register(SocialSection)
class SocialSectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'link', 'created_date', 'updated_date')
    list_filter = ('link', )
    search_fields = ('name', 'alternative_link', 'link', 'alternative_logo')
    readonly_fields = ('created_date', 'updated_date')


@admin.register(SiteFooter)
class SiteFooterAdmin(admin.ModelAdmin):
    list_display = ('id', 'legal_sentence_of_right_of_ownership', 'link_of_right_of_ownership_site', 'created_date', 'updated_date')
    list_filter = ('links_section', 'social_section', 'link_of_right_of_ownership_site',)
    search_fields = ('legal_sentence_of_right_of_ownership', 'link_of_right_of_ownership_site')
    readonly_fields = ('created_date', 'updated_date')


@admin.register(SiteTheme)
class SiteThemeAdmin(admin.ModelAdmin):
    list_display = ('id', 'theme_name', 'black', 'white', 'gray', 'primaryColor', 'secondaryColor', 'gradientFirstColor', 'gradientSecondColor', 'type_theme')
    search_fields = ('theme_name', 'black', 'white', 'gray', 'primaryColor', 'secondaryColor', 'gradientFirstColor', 'gradientSecondColor', 'type_theme')
    list_filter = ('theme_name', 'black', 'white', 'gray', 'primaryColor', 'secondaryColor', 'gradientFirstColor', 'gradientSecondColor', 'type_theme')
    

@admin.register(SiteStructure)
class SiteStructureAdmin(admin.ModelAdmin):
    list_display = ('id', 'site_name', 'header', 'fooer', 'dark_theme', 'light_theme', 'created_date', 'updated_date')
    list_filter = ('site_name', 'header', 'fooer', 'dark_theme', 'light_theme',)
    search_fields = ('site_name',)
    readonly_fields = ('created_date', 'updated_date')



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




@admin.register(BoxManagment)
class BoxManagmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'box_name', 'name_in_view', 'box_location', 'box_priority', 'content_type', 
                   'item_count', 'box_item_type', 'status',)
    list_filter = ('box_location', 'box_priority', 'content_type', 'categorys', 'sub_categorys', 
                   'sub_sub_categorys' , 'tags', 'item_count', 'box_item_type', 
                   'status', 'supervisor_to_add', 'back_ground_color_code',)
    search_fields = ('box_name', 'name_in_view', 'box_location', 'content_type', 'categorys', 'sub_categorys', 
                  'sub_sub_categorys' , 'tags', 'supervisor_to_add', )
    readonly_fields = ('created_date', 'updated_date')


@admin.register(LocationBox)
class LocationBoxAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', )
    search_fields = ('name',)
    

@admin.register(ItemsBoxByHand)
class ItemsBoxByHandAdmin(admin.ModelAdmin):
    list_display = ('id',  'user', 'box', 'video',)
    list_filter = ( 'user', 'box', 'video',)
    search_fields = ( 'user', 'box', 'video',)
    

@admin.register(OfferForBoxFromOwnerChannel)
class OfferForBoxFromOwnerChannelAdmin(admin.ModelAdmin):
    list_display = ('id', 'proposing_user', 'video', 'box', 'is_accept', 'supervisor',)
    list_filter = ('proposing_user', 'video', 'box', 'is_accept', 'supervisor',)
    search_fields = ('proposing_user', 'video', 'box', 'is_accept', 'supervisor',)
    
    

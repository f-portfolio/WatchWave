
from django.db import models
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser, PermissionsMixin)
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
#from django.utils import timezone
from django.conf import settings

# Create your models here.

class SiteHeader(models.Model):
    name = models.CharField(max_length=300, unique=True, null=False, blank=False)
    logo = models.ImageField(null=True, blank=True)
    alternative_logo = models.CharField(null=True, blank=True, max_length=250)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ['-created_date']


class LinkSection(models.Model):
    name = models.CharField(max_length=300, null=False, blank=False)
    link = models.URLField( null=False, blank=False)
    alternative_link = models.CharField(null=True, blank=True, max_length=250)
    created_date = models.DateTimeField( auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ['-created_date']


class SocialSection(models.Model):
    name = models.CharField(max_length=300, null=False, blank=False)
    link = models.URLField(null=False, blank=False)
    alternative_link = models.CharField(null=True, blank=True, max_length=250)
    logo = models.ImageField(null=True, blank=True)
    alternative_logo = models.CharField(null=True, blank=True, max_length=250)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ['-created_date']


class SiteFooter(models.Model):
    links_section = models.ManyToManyField(LinkSection, related_name='links_section', null=True, blank=True)
    social_section = models.ManyToManyField(SocialSection, related_name='social_section', null=True, blank=True)
    legal_sentence_of_right_of_ownership = models.CharField(max_length=500, null=False, blank=False)
    link_of_right_of_ownership_site = models.URLField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def __str__(self) -> str:
        return self.legal_sentence_of_right_of_ownership

    class Meta:
        ordering = ['-created_date']


class SiteTheme(models.Model):
    THEME_FIELD_CHOICES = [
        ('dark', 'dark teheme'),
        ('light', 'light theme'),
    ]
    theme_name = models.CharField(max_length=100, unique=True, null=False, blank=False)
    background = models.CharField(max_length=7, null=False, blank=False)
    black = models.CharField(max_length=7, null=False, blank=False)
    white = models.CharField(max_length=7, null=False, blank=False)
    gray = models.CharField(max_length=7, null=False, blank=False)
    primaryColor = models.CharField(max_length=7, null=False, blank=False)
    secondaryColor = models.CharField(max_length=7, null=False, blank=False)
    gradientFirstColor = models.CharField(max_length=7, null=False, blank=False)
    gradientSecondColor = models.CharField(max_length=7, null=False, blank=False)
    type_theme = models.CharField(choices=THEME_FIELD_CHOICES, default='dark', )
    
    def __str__(self) -> str:
        return self.theme_name


class SiteStructure(models.Model):
    site_name = models.CharField(max_length=300, unique=True, null=False, blank=False)  # come after site url -> 192.158.24.17:3001/{site_name}/
    header = models.ForeignKey(SiteHeader, on_delete=models.SET_NULL, null=True, blank=True, related_name='heder')
    fooer = models.ForeignKey(SiteFooter, on_delete=models.SET_NULL, null=True, blank=True, related_name='footer')
    dark_theme = models.ForeignKey(SiteTheme, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'type_theme': 'dark'},related_name='dark_theme')
    light_theme = models.ForeignKey(SiteTheme, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'type_theme': 'light'},related_name='light_theme')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def __str__(self) -> str:
        return self.site_name

    class Meta:
        ordering = ['-created_date']



class BoxManagment (models.Model):
    box_item_type_FIELD_CHOICES = [
        ('atuo', 'automatic'),
        ('by hand', 'by hand'),
    ]
    content_type_FIELD_CHOICES = [
        ('video', 'video'),
        ('channel', 'channel'),
        ('audio', 'audio'),
    ]
    box_name = models.CharField(max_length=200, unique=True)  
    name_in_view = models.CharField(max_length=200, unique=True)  
    box_location = models.ForeignKey('Webpagestructure.LocationBox', on_delete=models.SET_NULL, null=True, blank=True, related_name='location', ) 
    box_priority = models.PositiveIntegerField()
    content_type =  models.CharField(choices=content_type_FIELD_CHOICES, default='video',)
    categorys = models.ForeignKey('attachments.Category', on_delete=models.SET_NULL, limit_choices_to={'type': 'category'}, null=True, blank=True, related_name='box_categorys', ) 
    sub_categorys = models.ForeignKey('attachments.Category', on_delete=models.SET_NULL, limit_choices_to={'type': 'sub_category'}, null=True, blank=True, related_name='box_sub_categorys', )
    sub_sub_categorys = models.ForeignKey('attachments.Category', on_delete=models.SET_NULL, limit_choices_to={'type': 'sub_sub_category'},  null=True, blank=True, related_name='box_sub_sub_categorys', )
    tags = models.ForeignKey("attachments.Tag", limit_choices_to={'confirm': True}, on_delete=models.SET_NULL, null=True, blank=True, related_name='box_tag')
    cach_time = models.IntegerField(default=60*10)
    item_count = models.IntegerField(default=6)
    box_item_type = models.CharField(choices=box_item_type_FIELD_CHOICES, default='atuo', )
    status = models.BooleanField(default=True,)
    supervisor_to_add = models.ForeignKey('accounts.Profile',  on_delete=models.SET_NULL, null=True, blank=True,  related_name='supervisor_to_add',)
    back_ground_color_code = models.CharField(max_length=7, null=True, blank=True, )  
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.box_name
    
    def get_categorys(self):
        return ", ".join([t.name for t in self.categorys.all()])
    
    def get_sub_categorys(self):
        return ", ".join([t.name for t in self.sub_categorys.all()])
    
    def get_sub_sub_categorys(self):
        return ", ".join([t.name for t in self.sub_sub_categorys.all()])
    
    class Meta:
        unique_together = ('box_name', 'box_location', 'box_priority')
        ordering = ['-created_date']
        

class LocationBox (models.Model):
    name = models.CharField(max_length=200, unique=True)  
    def __str__(self):
        return self.name
    

class ItemsBoxByHand (models.Model):
    user = models.ForeignKey('accounts.Profile',  on_delete=models.SET_NULL, null=True, blank=True, related_name='supervisor_to_fill_box',)
    box = models.ForeignKey('Webpagestructure.BoxManagment', limit_choices_to={'status': True},  on_delete=models.CASCADE, related_name='box',)
    video = models.ForeignKey('channels.VideoPost', limit_choices_to={'confirm_to_post': True, 'status':True}, related_name='box_vid', on_delete=models.CASCADE,)
    
    def __str__(self):
        return self.box.box_name
    
    class Meta:
        unique_together = ('box', 'video')
        ordering = ['-id']
     

class OfferForBoxFromOwnerChannel (models.Model):
    proposing_user = models.ForeignKey('accounts.Profile',  on_delete=models.CASCADE, related_name='proposing_user_to_fill_box',)
    video = models.ForeignKey('channels.VideoPost', limit_choices_to={'confirm_to_post': True, 'status':True}, related_name='offer_vid', on_delete=models.CASCADE,)
    box = models.ForeignKey('Webpagestructure.BoxManagment', limit_choices_to={'status': True},  on_delete=models.CASCADE, related_name='box_in_offer',)
    is_accept = models.BooleanField(default=False)
    supervisor =  models.ForeignKey('accounts.Profile', on_delete=models.SET_NULL, null=True, blank=True, related_name='supervisor_to_accept_post',)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('box', 'video')
        ordering = ['-created_date']



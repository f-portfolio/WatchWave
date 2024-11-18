from django.db import models
from django_resized import ResizedImageField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

# Create your models here.

class Tag(models.Model):
    name = models.CharField(max_length=30,  unique=True)
    confirm = models.BooleanField(default=False,)
    user_adder = models.ForeignKey('accounts.Profile',  on_delete=models.SET_NULL, null=True, blank=True, related_name='user_adder',)
    created_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        

class Language(models.Model):
    name = models.CharField(max_length=250, unique=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-name']
        

class Category(models.Model):
    name = models.CharField( max_length=250, unique=True)
    type = models.CharField( max_length=100, default='category')
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        


class LinkOfPosts(models.Model):
    name = models.CharField( max_length=100, unique=True)
    address = models.URLField()
    added_at = models.DateTimeField( auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-added_at']
        


class URL(models.Model):
    name = models.CharField(max_length=250,  unique=True)
    alternative = models.CharField(max_length=250)
    url = models.URLField( unique=True)
    caption = models.TextField(blank=True, null=True)
    type = models.ForeignKey('attachments.TypeOfURL', on_delete=models.CASCADE,)
    added_at = models.DateTimeField( auto_now_add=True)
    
    def __str__(self):
        return self.name  

    class Meta:
        ordering = ['-added_at']
        


class TypeOfURL(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        


class TypeOfAuthor(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        

class MetaKword (models.Model):
    name = name = models.CharField(max_length=70, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        


class ContentType (models.Model):
    name = models.CharField(max_length=200, unique=True)  
    def __str__(self):
        return self.name
    


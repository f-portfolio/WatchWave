
from django.db import models
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser, PermissionsMixin)
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create your models here.
class UserManager(BaseUserManager):
    """
    Custom User Model manager where username is the unique 
    identifiers for authentication instead of usernames.
    """
    def create_user(self, username, password, **extra_fields):
        """
        create and save a user with the given username and password and extra_fields.
        """
        if not username:
            raise ValueError(-('the username must be set'))
        # email = self.normalize_email(email)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, username, password, **extra_fields):
        """
        create and save a superuser with the given username and password.
        """
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_supervisor', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_verified', True)
        
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(-('superuser must have is_superuser=True'))
        if extra_fields.get('is_supervisor') is not True:
            raise ValueError(-('supervisor must have is_supervisor=True'))
        if extra_fields.get('is_staff') is not True:
            raise ValueError(-('staff must have is_staff=True'))
        if extra_fields.get('is_verified') is not True:
            raise ValueError(-('staffuser must have is_verified=True'))
        return self.create_user(username, password, **extra_fields)

    def create_supervisor(self, username, password, **extra_fields):
        extra_fields.setdefault('is_supervisor', True)
        extra_fields.setdefault('is_staff', True)
        
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(-('superuser must have is_superuser=True'))
        if extra_fields.get('is_supervisor') is not True:
            raise ValueError(-('supervisor must have is_supervisor=True'))
        if extra_fields.get('is_staff') is not True:
            raise ValueError(-('staff must have is_staff=True'))
        return self.create_user(username, password, **extra_fields)
    
class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User Model for app
    """
    username = models.CharField(max_length=255, unique=True)
    
    is_superuser = models.BooleanField( default=False)
    is_supervisor = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    
    group_permissions = models.ForeignKey('GroupPermission', on_delete=models.SET_NULL, related_name='group_permissions', null=True, blank=True)
    
    REQUIRED_FIELDS = [] #filling requaried fields
    USERNAME_FIELD = 'username'
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    objects = UserManager()

    def __str__(self) -> str:
        return self.username

    class Meta:
        ordering = ['-updated_date']
        


class Permission(models.Model):
    name = models.CharField(max_length=100,  unique=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.name


class GroupPermission(models.Model):
    name = models.CharField(max_length=100,  unique=True)
    permissions = models.ManyToManyField(Permission, related_name='permissions')
    
    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    image = models.ImageField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    sex = models.CharField(max_length=32, choices=[('man', 'man'), ('woman', 'woman'), ('I prefer not to say', 'I prefer not to say')], null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    province = models.CharField( max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    job = models.CharField(max_length=255, null=True, blank=True)
    education = models.CharField(max_length=255, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'user'
    REQUIRED_FIELDS = [] 

    def __str__(self) -> str:
        return self.user.username

    class Meta:
        ordering = ['-updated_date']
        

@receiver(post_save, sender=User)
def save_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance)
        if len(instance.username) == 11 and instance.username.isdigit():
            profile.first_name = instance.username[7::] + '***' + instance.username[0:4]
        else:
            profile.first_name = instance.username
        profile.save()


class PromotionRequest(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='promotion_requests')
    requested_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(null=True, blank=True)  # None means pending, True means approved, False means rejected

    def __str__(self):
        return f"Promotion request for {self.user.user.username}"
    


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from easy_select2 import Select2
from .models import *  # Import your models

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('id', 'username', 'is_superuser', 'is_supervisor', 'is_staff', 'is_verified', 'created_date', 'last_login')
    list_filter = ('username', 'is_superuser', 'is_supervisor', 'is_staff', 'is_verified', 'group_permissions', 'created_date', 'last_login')
    search_fields = ('username', 'group_permissions__name')
    date_hierarchy = 'created_date'
    ordering = ('username', )
    fieldsets = (
        ('Authentication', {
            "fields": (
                    'username', 'password'
            ), 
        }), 
        ('permissions', {
            "fields": ('is_superuser', 'is_supervisor', 'is_staff', 'is_verified', 'group_permissions',), 
        }), 
        ('group permissions', {
            "fields": ('groups', 'user_permissions'), 
        }), 
        ('important date', {
            "fields": ('last_login',), 
        }), 
    )
    add_fieldsets = (
         (None, {
            "classes": ('wide', ), 
            "fields": ('username', 'password1', 'password2', 'is_superuser', 'is_supervisor', 'is_staff',), 
        }), 
    )


admin.site.register(User, CustomUserAdmin)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'created_date', 'updated_date')
    search_fields = ('first_name', 'last_name', )
    readonly_fields = ('created_date', 'updated_date')

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'user':
            kwargs['widget'] = Select2()
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # If the user is a superuser, show all profiles
        if request.user.is_superuser:
            return qs
        # Otherwise, restrict to the user's own profile
        return qs.filter(user=request.user)
    

@admin.register(PromotionRequest)
class PromotionRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'requested_at', 'is_approved')
    list_filter = ('is_approved', 'requested_at')
    search_fields = ('user__username',)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('name', )
    search_fields = ('name',)


@admin.register(GroupPermission)
class GroupPermissionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name', 'permissions')
    search_fields = ('name', 'permissions__name')

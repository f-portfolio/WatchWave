from django.contrib import admin
from .models import *

@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'owner', 'subscribe_count', 'is_favorite', 'activation', 'created_date', 'updated_date')
    search_fields = ('name', 'owner__user__username', 'categorys')
    list_filter = ('owner', 'activation', 'is_favorite', 'created_date', 'categorys')
    readonly_fields = ('subscribe_count', 'created_date', 'updated_date')
    #filter_horizontal = ('admins', 'socials_address')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'channel')
    search_fields = ('user__user__username', 'channel__name')
    list_filter = ('channel', 'user')


@admin.register(VideoPost)
class VideoPostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'channel', 'publisher', 'status', 'confirm_to_post', 'is_pined', 'created_date', 'updated_date', 'published_date')
    search_fields = ('title', 'channel__name', 'publisher__user__username', 'tags__name', 'categorys__name')
    list_filter = ('status', 'confirm_to_post', 'is_pined', 'publisher', 'channel', 'published_date', 'tags', 'categorys', 'sub_categorys', 'sub_sub_categorys')
    readonly_fields = ('counted_views', 'counted_like', 'counted_dislike', 'counted_save', 'counted_share', 'created_date', 'updated_date')
    filter_horizontal = ('tags',)

    def save_model(self, request, obj, form, change):
        obj.save()  
        form.save_m2m()

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'video_post', 'comment', 
                    'uper_comment', 'confirm_to_comment', 
                    'supervisor_to_confirm',
                    'created_date', 'updated_date')
    search_fields = ('user__user__username', 'video_post__title', 
                     'comment', 'uper_comment')
    list_filter = ('confirm_to_comment', 'user')


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'video_post')
    search_fields = ('user__user__username', 'video_post__title')
    list_filter = ('user', )


@admin.register(Dislike)
class DislikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'video_post')
    search_fields = ('user__user__username', 'video_post__title')
    list_filter = ('user', )


@admin.register(Save)
class SaveAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'video_post')
    search_fields = ('user__user__username', 'video_post__title')
    list_filter = ('user', )

@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'video', 'timestamp', 'percentage_watched', 'last_viewed')
    search_fields = ('channel__name', 'video__title')
    list_filter = ('user', 'last_viewed',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'message', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'message')
    readonly_fields = ('created_at',)

    def user_username(self, obj):
        return obj.user.username
    user_username.admin_order_field = 'user'  # Allows column order sorting
    user_username.short_description = 'User Username'  # Renames column head


@admin.register(PlayList)
class PlayListAdmin(admin.ModelAdmin):
    list_display = ['id', 'package_name', 'channel', 'creator', 'created_date', 'updated_date']
    search_fields = ['package_name', 'package_description', 'play_list_videos__title', 'channel__name', 'creator__user__username']
    filter_horizontal = ['play_list_videos']
    list_filter = ('creator', 'channel')

    def save_model(self, request, obj, form, change):
        # Save the instance to get an ID before accessing many-to-many fields
        if not obj.pk:
            super().save_model(request, obj, form, change)
        form.save_m2m()


@admin.register(SpecialSection)
class SpecialSectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'creator', 'section_name')
    search_fields = ('creator__username', 'special_item__title', 'section_name')
    list_filter = ('creator',)


@admin.register(AdminsOfChannel)
class AdminsOfChannelAdmin(admin.ModelAdmin):
    list_display = ('id', 'admin', 'user_adder', 'channel')
    search_fields = ('admin__username', 'channel__name')
    list_filter = ('channel', 'user_adder')


@admin.register(SocialOfChanne)
class SocialOfChanneAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user_adder', 'channel')
    search_fields = ('name', 'channel__name', 'user_adder__username')
    list_filter = ('channel', 'user_adder')

from django.db import models
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_resized import ResizedImageField
from attachments.models import Tag, Category, Language
from accounts.models import Profile
from django.core.exceptions import ValidationError
import re
import moviepy.editor as mp
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from rest_framework import serializers
from django.utils.timezone import now


def validate_video_size(value):
    max_size = 2 * 1024 * 1024 * 1024  # 2GB in bytes
    if value.size > max_size:
        raise ValidationError("The maximum file size that can be uploaded is 2GB.")
    
    
class Channel(models.Model):
    id = models.AutoField(primary_key=True)
    avatar = ResizedImageField(force_format="WEBP", quality=75, upload_to="images/", null=True, blank=True) 
    banner = models.FileField(upload_to="images/", null=True, blank=True) 
    owner = models.ForeignKey('accounts.Profile', on_delete=models.CASCADE, related_name='channel_owner')
    name = models.CharField(max_length=100, unique=True)
    handle = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(null=True, blank=True, )
    categorys = models.ForeignKey('attachments.Category', on_delete=models.SET_NULL, null=True, blank=True, related_name='channel_categorys') 
    subscribe_count = models.IntegerField( null=True, default=0)
    confirm_to_channel = models.BooleanField(default=True,)
    supervisor_to_confirm = models.ForeignKey('accounts.Profile',  on_delete=models.SET_NULL, null=True, blank=True, related_name='supervisor_to_confirm')
    
    is_favorite = models.BooleanField(default=False,)
    supervisor_to_favorited = models.ForeignKey('accounts.Profile', on_delete=models.SET_NULL, null=True, blank=True, related_name='favorited_posts_vod')
    
    counted_view = models.IntegerField(null=True, default=0)
    activation = models.BooleanField(default=True,)
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def get_absolute_api_url(self):
        return reverse("channels:api-v1:channel-detail", kwargs={"pk": self.pk})
    
    def get_categorys(self):
        return ", ".join([t.name for t in self.categorys.all()])
    
    def save(self, *args, **kwargs):
        if self.supervisor_to_favorited and self.supervisor_to_favorited.user.is_supervisor \
            and self.is_favorite:
            self.supervisor_to_favorited = self.supervisor_to_favorited
        
        if self.is_favorite == False:
            self.supervisor_to_favorited = None
            self.is_favorite = False
        
        if self.is_favorite == True and self.supervisor_to_favorited is None:
            self.supervisor_to_favorited = None
            self.is_favorite = False
        
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_date']
        

class AdminsOfChannel(models.Model):
    user_adder = models.ForeignKey('accounts.Profile', related_name='user_adder_admin', on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, limit_choices_to={'confirm_to_channel': True, 'activation':True}, on_delete=models.CASCADE)
    admin = models.ForeignKey('accounts.Profile', related_name='admins', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.admin) 

    class Meta:
        unique_together = ('admin', 'channel')
    
    def clean(self):
        super(AdminsOfChannel, self).clean()
        if AdminsOfChannel.objects.filter(admin=self.admin, channel=self.channel).exists():
            raise serializers.ValidationError('This user has already been added as an admin of this channel.')

class SocialOfChanne(models.Model):
    user_adder = models.ForeignKey('accounts.Profile', related_name='user_adder_social', on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, limit_choices_to={'confirm_to_channel': True, 'activation':True}, on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    link = models.URLField(unique=True)
    
    def __str__(self):
        return self.name
    

class Subscription(models.Model):
    user = models.ForeignKey('accounts.Profile', on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, limit_choices_to={'confirm_to_channel': True, 'activation':True}, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.user.username} subscribed to {self.channel.name}'

    class Meta:
        verbose_name = _('Subscription')
        verbose_name_plural = _('Subscription')
        constraints = [
            models.UniqueConstraint(fields=['user', 'channel'], name='unique_subscription')
        ]

    def save(self, *args, **kwargs):
        #self.clean()
        super().save(*args, **kwargs)


class VideoPost(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    publisher = models.ForeignKey('accounts.Profile', on_delete=models.CASCADE, related_name='posts_publisher')
    slog = models.CharField( max_length=25, null=True, blank=True,)
    video = models.FileField(upload_to='videos/', validators=[validate_video_size])
    hls_master_playlist = models.CharField(max_length=255, blank=True, null=True)
    language_video = models.ForeignKey('attachments.Language', on_delete=models.SET_NULL, null=True, blank=True, related_name='language_video')
    title = models.CharField(max_length=150, null=True, blank=True, unique=True)
    snippet = models.TextField(max_length=150, null=True, blank=True,)
    meta_description = models.CharField( max_length=150, null=True, blank=True)
    description = models.TextField(max_length=5000, null=True, blank=True)
    reference = models.CharField(max_length=300, null=True, blank=True)
    cast = models.CharField(max_length=300, null=True, blank=True) 
    cover = models.ImageField(upload_to='cover/', blank=True, null=True)
    categorys = models.ForeignKey('attachments.Category', on_delete=models.SET_NULL, limit_choices_to={'type': 'category'}, null=True, blank=True, related_name='categorys', ) 
    sub_categorys = models.ForeignKey('attachments.Category', on_delete=models.SET_NULL, limit_choices_to={'type': 'sub_category'}, null=True, blank=True, related_name='sub_categorys', )
    sub_sub_categorys = models.ForeignKey('attachments.Category', on_delete=models.SET_NULL, limit_choices_to={'type': 'sub_sub_category'},  null=True, blank=True, related_name='sub_sub_categorys', )
    tags = models.ManyToManyField("attachments.Tag", limit_choices_to={'confirm': True}, related_name='posts_tag')
    
    counted_views = models.IntegerField(default=0)
    counted_like = models.IntegerField(default=0)
    counted_dislike = models.IntegerField(default=0)
    counted_save = models.IntegerField(default=0)
    counted_share = models.IntegerField(default=0)
    status = models.BooleanField(default=False,)
    
    confirm_to_post = models.BooleanField(default=False,)
    supervisor_to_confirm = models.ForeignKey('accounts.Profile', on_delete=models.SET_NULL, null=True, blank=True, related_name='confirmed_posts')

    is_pined = models.BooleanField (default=False,)
    supervisor_to_pined = models.ForeignKey('accounts.Profile', on_delete=models.SET_NULL, null=True, blank=True, related_name='pined_video_posts')
    
    duration = models.PositiveIntegerField(default=1)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    published_date = models.DateTimeField(null=True, blank=True,)
    
    def __str__(self):
        return self.title
    
    def get_absolute_api_url(self):
        return reverse("channels:api-v1:videopost-detail", kwargs={"pk": self.pk})
    
    def get_duration(self):
        try:
            video = mp.VideoFileClip(self.video_file.path)
            return video.duration
        except:
            return 0
    
    def clean(self):
        super().clean()
        #if self.tags.count() > 3:
        if self.pk and self.tags.count() > 3:
            raise ValidationError("The number of tags should not exceed 3.")

    def save(self, *args, **kwargs):
        if re.findall(r' style="(.*?)"', self.description):
            pattern = r' style="(.*?)"'
            replacement = ''
            self.description = re.sub(pattern, replacement, self.description)

        if re.findall(r''' style=".*
(.*?)"''', self.description):
            pattern = r''' style=".*
(.*?)"'''
            replacement = ''
            self.description = re.sub(pattern, replacement, self.description)

        if self.supervisor_to_confirm and self.supervisor_to_confirm.user.is_supervisor \
            and self.confirm_to_post:
            self.supervisor_to_confirm = self.supervisor_to_confirm
        if self.confirm_to_post == False:
            self.supervisor_to_confirm = None
            self.confirm_to_post = False

        if self.published_date and self.published_date.date() == now().date():
            self.status = True
        else:
            self.status = False
        
        if self.supervisor_to_pined and self.supervisor_to_pined.user.is_supervisor \
            and self.is_pined:
            self.supervisor_to_pined = self.supervisor_to_pined
        if self.is_pined == False:
            self.supervisor_to_pined = None
            self.is_pined = False
        
        if not self.meta_description:
            self.meta_description = self.snippet    

        super().save(*args, **kwargs)
        
    def get_tags(self):
        return ", ".join([t.name for t in self.tags.all()])
    
    def get_categorys(self):
        return ", ".join([t.name for t in self.categorys.all()])
    
    class Meta:
        ordering = ['-published_date']
        
        

class Like(models.Model):
    user = models.ForeignKey('accounts.Profile', on_delete=models.CASCADE)
    video_post = models.ForeignKey(VideoPost, limit_choices_to={'confirm_to_post': True, 'status':True}, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.user.username} likes {self.video_post.title}'
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'video_post'], name='unique_like')
        ]


class Dislike(models.Model):
    user = models.ForeignKey('accounts.Profile', on_delete=models.CASCADE)
    video_post = models.ForeignKey(VideoPost, limit_choices_to={'confirm_to_post': True, 'status':True}, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.user.username} likes {self.video_post.title}'
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'video_post'], name='unique_dislike')
        ]


class Save(models.Model):
    user = models.ForeignKey('accounts.Profile', on_delete=models.CASCADE)
    video_post = models.ForeignKey(VideoPost, limit_choices_to={'confirm_to_post': True, 'status':True}, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.user.username} likes {self.video_post.title}'

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'video_post'], name='unique_save')
        ]


class Comment(models.Model):
    user = models.ForeignKey('accounts.Profile', on_delete=models.CASCADE, related_name='user_write_comments',)
    video_post = models.ForeignKey(VideoPost, limit_choices_to={'confirm_to_post': True, 'status':True}, on_delete=models.CASCADE)
    uper_comment = models.ForeignKey('self', limit_choices_to={'confirm_to_comment': True}, on_delete=models.SET_NULL, related_name='uper_comments', null=True, blank=True)
    comment = models.TextField()
    
    confirm_to_comment = models.BooleanField(default=False,)
    supervisor_to_confirm = models.ForeignKey('accounts.Profile', on_delete=models.SET_NULL, null=True, blank=True, 
                                              related_name='confirmed_comments',)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.comment[:20]

    def save(self, *args, **kwargs):
        if re.findall(r' style="(.*?)"', self.comment):
            pattern = r' style="(.*?)"'
            replacement = ''
            self.comment = re.sub(pattern, replacement, self.comment)

        if re.findall(r''' style=".*
(.*?)"''', self.comment):
            pattern = r''' style=".*
(.*?)"'''
            replacement = ''
            self.comment = re.sub(pattern, replacement, self.comment)

        if self.supervisor_to_confirm and self.supervisor_to_confirm.user.is_staff \
            and self.supervisor_to_confirm:
            self.supervisor_to_confirm = self.supervisor_to_confirm
        elif self.supervisor_to_confirm == False:
            self.supervisor_to_confirm = None
            self.supervisor_to_confirm = False
        
        super().save(*args, **kwargs)
    

class History(models.Model):
    user = models.ForeignKey('accounts.Profile', on_delete=models.CASCADE)
    video = models.ForeignKey(VideoPost, limit_choices_to={'confirm_to_post': True, 'status':True}, on_delete=models.CASCADE)
    timestamp = models.CharField(default='0')  # Time up to which the user has watched the video
    percentage_watched = models.FloatField(default=0)  # Percentage of the video watched
    last_viewed = models.DateTimeField(auto_now=True)  # Auto-updates to the current time whenever the record is saved

    class Meta:
        ordering = ['-id'] 
        
    # calculate the percentage of the video watched before saving the history object
    def save(self, *args, **kwargs):
        #video_duration = self.video.duration
        # create a new field in the history model to store the percentage of the video watched
        #self.percentage_watched = (int(self.timestamp) / video_duration) * 100
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.user.user.username} watched {self.video.id} up to {self.timestamp}s ({self.percentage_watched}%)"


class Notification(models.Model):
    user = models.ForeignKey('accounts.Profile', on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.user.username}"

    class Meta:
        ordering = ['-created_at']
        

class PlayList(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    creator = models.ForeignKey('accounts.Profile', on_delete=models.CASCADE, related_name='play_list_creator')
    package_name = models.CharField(max_length=150, null=True, blank=True, unique=True)
    package_description = models.TextField(max_length=5000, null=True, blank=True)
    play_list_videos = models.ManyToManyField(VideoPost, limit_choices_to={'confirm_to_post': True, 'status':True}, related_name='play_list_videos')
    created_date = models.DateTimeField( auto_now_add=True)
    updated_date = models.DateTimeField( auto_now=True)
    
    def __str__(self):
        return self.package_name
    
    def save(self, *args, **kwargs):
        if re.findall(r' style="(.*?)"', self.package_description):
            pattern = r' style="(.*?)"'
            replacement = ''
            self.package_description = re.sub(pattern, replacement, self.package_description)

        if re.findall(r''' style=".*
(.*?)"''', self.package_description):
            pattern = r''' style=".*
(.*?)"'''
            replacement = ''
            self.package_description = re.sub(pattern, replacement, self.package_description)

        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_date']


class SpecialSection(models.Model):
    creator = models.ForeignKey('accounts.Profile', on_delete=models.CASCADE, related_name='special_item_list_creator',  null=True, blank=True, )
    section_name = models.CharField(max_length=150)
    special_item = models.ForeignKey(VideoPost, limit_choices_to={'confirm_to_post': True, 'status':True}, related_name='posts_vid', on_delete=models.CASCADE,)
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField( auto_now=True)
    
    def __str__(self):
        return self.section_name
    
    def get_special_item(self):
        return ", ".join([t.title for t in self.special_item.all()])
   

class TastM(models.Model):
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.name
    
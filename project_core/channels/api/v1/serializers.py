from channels.models import *
from rest_framework import serializers
from django.core.exceptions import PermissionDenied
from accounts.models import Profile
from attachments.api.v1.serializers import TagSerializer, CategorySerializer, LanguageSerializer
from django.contrib.auth import get_user_model
current_user = get_user_model()

    

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'first_name', 'last_name', 'image']


class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = [
            'id', 'avatar', 'banner', 'owner', 'name', 'categorys',
            'handle', 'description', 'subscribe_count', 'counted_view',
            'activation', 'is_favorite', 
            'supervisor_to_favorited', 'supervisor_to_confirm', 
            'confirm_to_channel', 'created_date', 'updated_date'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if ('request' in self.context 
            and self.context['request'].user.is_authenticated 
            and self.context['request'].user.is_verified
            and self.context['request'].user.is_staff 
            and not self.context['request'].user.is_supervisor 
            and not self.context['request'].user.is_superuser):
            self.fields['activation'].read_only = True
            self.fields['is_favorite'].read_only = True
            self.fields['supervisor_to_favorited'].read_only = True
            self.fields['supervisor_to_confirm'].read_only = True
            self.fields['confirm_to_channel'].read_only = True
            self.fields['subscribe_count'].read_only = True
            self.fields['counted_view'].read_only = True

        elif ('request' in self.context 
            and self.context['request'].user.is_authenticated 
            and self.context['request'].user.is_verified
            and (self.context['request'].user.is_supervisor or self.context['request'].user.is_superuser)):
            self.fields['confirm_to_channel'].read_only = True
            self.fields['supervisor_to_confirm'].read_only = True
            self.fields['activation'].read_only = True
            self.fields['subscribe_count'].read_only = True
            self.fields['counted_view'].read_only = True

        else:
            for field in self.Meta.fields:
                self.fields[field].read_only = True

    def to_representation(self, instance):
        request = self.context.get('request')
        rep = super().to_representation(instance)
        if instance.avatar:
            rep['avatar'] = instance.avatar.url.split('/media/', 1)[-1]
            rep['avatar'] = 'media/' + rep['avatar']
        if instance.banner:
            rep['banner'] = instance.banner.url.split('/media/', 1)[-1]
            rep['banner'] = 'media/' + rep['banner']
        rep['owner'] = ProfileSerializer(instance.owner, context={'request': request}).data
        rep['categorys'] = CategorySerializer(instance.categorys, context={'request':request}).data
        rep['supervisor_to_favorited'] = ProfileSerializer(instance.supervisor_to_favorited, context={'request': request}).data
        rep['supervisor_to_confirm'] = ProfileSerializer(instance.supervisor_to_confirm, context={'request': request}).data
        return rep
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request.user.is_staff:
            user = request.user.profile
            validated_data['owner'] = user
        channel = Channel.objects.create(**validated_data)
        return channel

    def update(self, instance, validated_data):
        print(validated_data)
        # Update name and description fields (skip if None or empty)
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.categorys = validated_data.get('categorys', instance.categorys)
        
        instance.save()
        return instance
    
    def update(self, instance, validated_data):
        if validated_data['avatar'] is None:
            validated_data['avatar'] = instance.avatar
        
        if validated_data['banner'] is None:
            validated_data['banner'] = instance.banner
        #print("#######################################################")
        return super().update(instance, validated_data)

class ChannelEditBodySerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = ['id', 'avatar', 'banner', 'owner', 'name', 'categorys',
            'handle', 'description', 'subscribe_count', 'counted_view',
            'activation', 'is_favorite', 
            'supervisor_to_favorited', 'supervisor_to_confirm', 
            'confirm_to_channel', 'created_date', 'updated_date',]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if ('request' in self.context 
            and self.context['request'].user.is_authenticated 
            and self.context['request'].user.is_verified
            and self.context['request'].user.is_staff 
            and not self.context['request'].user.is_supervisor 
            and not self.context['request'].user.is_superuser):
            self.fields['activation'].read_only = True
            self.fields['is_favorite'].read_only = True
            self.fields['supervisor_to_favorited'].read_only = True
            self.fields['supervisor_to_confirm'].read_only = True
            self.fields['confirm_to_channel'].read_only = True
            self.fields['subscribe_count'].read_only = True
            self.fields['counted_view'].read_only = True
            self.fields['banner'].read_only = True
            self.fields['avatar'].read_only = True

        elif ('request' in self.context 
            and self.context['request'].user.is_authenticated 
            and self.context['request'].user.is_verified
            and (self.context['request'].user.is_supervisor or self.context['request'].user.is_superuser)):
            self.fields['confirm_to_channel'].read_only = True
            self.fields['supervisor_to_confirm'].read_only = True
            self.fields['activation'].read_only = True
            self.fields['subscribe_count'].read_only = True
            self.fields['counted_view'].read_only = True
            self.fields['banner'].read_only = True
            self.fields['avatar'].read_only = True

        else:
            for field in self.Meta.fields:
                self.fields[field].read_only = True

    def to_representation(self, instance):
        request = self.context.get('request')
        rep = super().to_representation(instance)
        rep['owner'] = ProfileSerializer(instance.owner, context={'request': request}).data
        rep['categorys'] = CategorySerializer(instance.categorys, context={'request':request}).data
        if instance.avatar:
            rep['avatar'] = instance.avatar.url.split('/media/', 1)[-1]
            rep['avatar'] = 'media/' + rep['avatar']
        if instance.banner:
            rep['banner'] = instance.banner.url.split('/media/', 1)[-1]
            rep['banner'] = 'media/' + rep['banner']
        rep['supervisor_to_favorited'] = ProfileSerializer(instance.supervisor_to_favorited, context={'request': request}).data
        rep['supervisor_to_confirm'] = ProfileSerializer(instance.supervisor_to_confirm, context={'request': request}).data
        return rep
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request.user.is_staff:
            user = request.user.profile
            validated_data['owner'] = user
        channel = Channel.objects.create(**validated_data)
        return channel

    def update(self, instance, validated_data):
        print(validated_data)
        # Update name and description fields (skip if None or empty)
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.categorys = validated_data.get('categorys', instance.categorys)
        
        instance.save()
        return instance

class ChannelEditAvatarSerializer(serializers.ModelSerializer): 
    class Meta:
        model = Channel
        fields = ['id', 'avatar', 'banner', 'owner', 'name', 'categorys',
            'handle', 'description', 'subscribe_count', 'counted_view',
            'activation', 'is_favorite', 
            'supervisor_to_favorited', 'supervisor_to_confirm', 
            'confirm_to_channel', 'created_date', 'updated_date']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if ('request' in self.context 
            and self.context['request'].user.is_authenticated 
            and self.context['request'].user.is_verified
            and self.context['request'].user.is_staff 
            and not self.context['request'].user.is_supervisor 
            and not self.context['request'].user.is_superuser):
            self.Meta.read_only_fields = ['id', 'banner', 'owner', 'name', 'categorys',
                                        'handle', 'description', 'subscribe_count', 'counted_view',
                                        'activation', 'is_favorite', 
                                        'supervisor_to_favorited', 'supervisor_to_confirm', 
                                        'confirm_to_channel', 'created_date', 'updated_date']
            
        elif ('request' in self.context 
            and self.context['request'].user.is_authenticated 
            and self.context['request'].user.is_verified
            and (self.context['request'].user.is_supervisor or self.context['request'].user.is_superuser)):
            self.Meta.read_only_fields = ['id', 'banner', 'owner', 'name', 'categorys',
                                        'handle', 'description', 'subscribe_count', 'counted_view',
                                        'activation', 'is_favorite', 
                                        'supervisor_to_favorited', 'supervisor_to_confirm', 
                                        'confirm_to_channel', 'created_date', 'updated_date']
            
        else:
            for field in self.Meta.fields:
                self.fields[field].read_only = True

    def to_representation(self, instance):
        request = self.context.get('request')
        rep = super().to_representation(instance)
        rep['owner'] = ProfileSerializer(instance.owner, context={'request': request}).data
        rep['categorys'] = CategorySerializer(instance.categorys, context={'request':request}).data
        if instance.avatar:
            rep['avatar'] = instance.avatar.url.split('/media/', 1)[-1]
            rep['avatar'] = 'media/' + rep['avatar']
        if instance.banner:
            rep['banner'] = instance.banner.url.split('/media/', 1)[-1]
            rep['banner'] = 'media/' + rep['banner']
        rep['supervisor_to_favorited'] = ProfileSerializer(instance.supervisor_to_favorited, context={'request': request}).data
        rep['supervisor_to_confirm'] = ProfileSerializer(instance.supervisor_to_confirm, context={'request': request}).data
        return rep
    
class ChannelBanerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = [
            'id', 'avatar', 'banner', 'owner', 'name', 'categorys',
            'handle', 'description', 'subscribe_count', 'counted_view',
            'activation', 'is_favorite', 
            'supervisor_to_favorited', 'supervisor_to_confirm', 
            'confirm_to_channel', 'created_date', 'updated_date'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if ('request' in self.context 
            and self.context['request'].user.is_authenticated 
            and self.context['request'].user.is_verified
            and self.context['request'].user.is_staff 
            and not self.context['request'].user.is_supervisor 
            and not self.context['request'].user.is_superuser):
            self.Meta.read_only_fields = ['id', 'avatar', 'owner', 'name', 'categorys',
                                        'handle', 'description', 'subscribe_count', 'counted_view',
                                        'activation', 'is_favorite', 
                                        'supervisor_to_favorited', 'supervisor_to_confirm', 
                                        'confirm_to_channel', 'created_date', 'updated_date']

        elif ('request' in self.context 
            and self.context['request'].user.is_authenticated 
            and self.context['request'].user.is_verified
            and (self.context['request'].user.is_supervisor or self.context['request'].user.is_superuser)):
            self.Meta.read_only_fields = ['id', 'avatar', 'owner', 'name', 'categorys',
                                        'handle', 'description', 'subscribe_count', 'counted_view',
                                        'activation', 'is_favorite', 
                                        'supervisor_to_favorited', 'supervisor_to_confirm', 
                                        'confirm_to_channel', 'created_date', 'updated_date']
        else:
            for field in self.Meta.fields:
                self.fields[field].read_only = True

    def to_representation(self, instance):
        request = self.context.get('request')
        rep = super().to_representation(instance)
        rep['owner'] = ProfileSerializer(instance.owner, context={'request': request}).data
        rep['categorys'] = CategorySerializer(instance.categorys, context={'request':request}).data
        if instance.avatar:
            rep['avatar'] = instance.avatar.url.split('/media/', 1)[-1]
            rep['avatar'] = 'media/' + rep['avatar']
        if instance.banner:
            rep['banner'] = instance.banner.url.split('/media/', 1)[-1]
            rep['banner'] = 'media/' + rep['banner']
        rep['supervisor_to_favorited'] = ProfileSerializer(instance.supervisor_to_favorited, context={'request': request}).data
        rep['supervisor_to_confirm'] = ProfileSerializer(instance.supervisor_to_confirm, context={'request': request}).data
        return rep
    

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'user', 'channel']
        read_only_fields = ['user']

    def to_representation(self,instance):
        request = self.context.get('request')
        rep = super().to_representation(instance)

        rep['user'] = ProfileSerializer(instance.user, context={'request':request}).data
        rep['channel'] = ChannelSerializer(instance.channel, context={'request':request}).data
        return rep
    
    def create(self, validated_data):
        request = self.context.get('request')
        # print('request.user ==> ', request.user)
        validated_data['user'] = request.user.profile
        return super().create(validated_data)
    
    def validate(self, data):
        request = self.context.get('request', None)
        if request:
            user = request.user.profile
            channel = data['channel']
            '''
            if user == channel.owner:
                raise serializers.ValidationError("The channel owner cannot subscribe to their own channel.")
            
            # Check if the user is an admin of the channel
            if AdminsOfChannel.objects.filter(channel=channel, admin=user).exists():
                raise serializers.ValidationError("Channel admins cannot subscribe to their own channel.")
            '''
            # Check if the user is already subscribed to the channel
            if Subscription.objects.filter(channel=channel, user=user).exists():
                raise serializers.ValidationError("The user is already subscribed to this channel.")
        return data



################################################ video_post ##################################################
read_only_fields_video_for_staff = ['slog', 'hls_master_playlist', 'counted_views', 
                                    'counted_like', 'counted_dislike', 'counted_save', 
                                    'counted_share', 'status', ]

read_only_fields_video_for_supervisor_or_superuser = ['hls_master_playlist', 'counted_views', 
                                                        'counted_like', 'counted_dislike', 
                                                        'counted_save', 'status', 'counted_share',]

read_only_fields_video_for_else = ['id', 'channel', 'publisher', 'slog', 'video', 'hls_master_playlist', 
                                    'language_video', 'title', 'snippet', 'meta_description', 'cover',
                                    'description', 'reference', 'cast', 'categorys', 'tags',
                                    'sub_categorys', 'sub_sub_categorys' , 
                                    'counted_views', 'counted_like', 'counted_dislike', 'counted_save', 
                                    'counted_share', 'status', 'confirm_to_post', 'supervisor_to_confirm', 
                                    'is_pined', 'supervisor_to_pined', 'duration', 
                                    'created_date', 'updated_date', 'published_date', ]

all_fields_video = ['id', 'channel', 'slog', 'video', 'hls_master_playlist', 
                'language_video', 'title', 'snippet', 'meta_description', 'cover',
                'description', 'reference', 'cast', 'categorys', 
                'sub_categorys', 'sub_sub_categorys', 'tags', 'word_count',
                'counted_views', 'counted_like', 'counted_dislike', 'counted_save', 
                'counted_share', 'status', 'confirm_to_post', 'supervisor_to_confirm', 
                'is_pined', 'supervisor_to_pined', 'duration', 
                'created_date', 'updated_date', 'published_date', ]

class VideoPostSerializer(serializers.ModelSerializer):
    word_count = serializers.SerializerMethodField(read_only=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if ('request' in self.context 
            and self.context['request'].user.is_authenticated 
            and self.context['request'].user.is_verified
            and self.context['request'].user.is_staff 
            and self.context['request'].user.is_supervisor == False
            and self.context['request'].user.is_superuser == False):
            
            self.Meta.read_only_fields = read_only_fields_video_for_staff
            
        elif ('request' in self.context 
            and self.context['request'].user.is_authenticated 
            and self.context['request'].user.is_verified
            and (self.context['request'].user.is_supervisor or self.context['request'].user.is_superuser)):
            self.Meta.read_only_fields = read_only_fields_video_for_supervisor_or_superuser

        else:
            self.Meta.read_only_fields = read_only_fields_video_for_else
    
    class Meta:
        model = VideoPost
        fields = all_fields_video
       
    def validate_tags(self, value):
        if len(value) > 3:
            raise serializers.ValidationError("The number of tags should not exceed 3.")
        return value

    def to_representation(self,instance):
        request = self.context.get('request')
        rep = super().to_representation(instance)
        # when call a serializer into another serializer should also pass the request
        rep['channel'] = ChannelSerializer(instance.channel, context={'request':request}).data
        rep['publisher'] = ProfileSerializer(instance.publisher, context={'request':request}).data
        if instance.video:
            rep['video'] = instance.video.url.split('/media/', 1)[-1]
            rep['video'] = 'media/' + rep['video']
        if instance.cover:
            rep['cover'] = instance.cover.url.split('/media/', 1)[-1]
            rep['cover'] = 'media/' + rep['cover']
        rep['language_video'] = LanguageSerializer(instance.language_video, context={'request':request}).data
        rep['categorys'] = CategorySerializer(instance.categorys, context={'request':request}).data
        rep['sub_categorys'] = CategorySerializer(instance.sub_categorys, context={'request':request}).data
        rep['sub_sub_categorys'] = CategorySerializer(instance.sub_sub_categorys, context={'request':request}).data
        rep['tags'] = TagSerializer(instance.tags.all(), context={'request':request}, many=True).data
        rep['supervisor_to_confirm'] = ProfileSerializer(instance.supervisor_to_confirm, context={'request':request}).data
        return rep
    
    def get_word_count(self, obj):
        return len(obj.description.split(' '))
    
    def create(self,validated_data):
        request = self.context.get('request')
        user = request.user.profile  # Assuming user has a profile

        channel = validated_data['channel']
        is_admin = AdminsOfChannel.objects.filter(channel=channel, admin=user).exists()
        if not (is_admin or user == channel.owner  or request.user.is_supervisor):
            raise PermissionDenied("You cannot post to a channel that you are not the owner or admin of.")
        
        validated_data['publisher'] = user

        if ('request' in self.context 
            and self.context['request'].user.is_authenticated 
            and self.context['request'].user.is_verified
            and self.context['request'].user.is_supervisor):
            validated_data['confirm_to_post'] = True
            validated_data['supervisor_to_confirm'] = Profile.objects.get(user__id=user.id)

        return super().create(validated_data)
    

    def update(self, instance, validated_data):
        instance.slog = validated_data.get('slog', instance.slog)
        instance.title = validated_data.get('title', instance.title)
        instance.snippet = validated_data.get('snippet', instance.snippet)
        instance.description = validated_data.get('description', instance.description)
        instance.reference = validated_data.get('reference', instance.reference)
        instance.cast = validated_data.get('cast', instance.cast)
        instance.cover = validated_data.get('cover', instance.cover)
        instance.categorys = validated_data.get('categorys', instance.categorys)
        instance.confirm_to_post = validated_data.get('confirm_to_post', instance.confirm_to_post)
        instance.supervisor_to_confirm = validated_data.get('supervisor_to_confirm', instance.supervisor_to_confirm)

        instance.save()
        if 'tags' in validated_data:
            instance.tags.set(validated_data.get('tags'))
        return instance
        
    def update(self, instance, validated_data):
        validated_data['video'] = instance.video
        validated_data['channel'] = instance.channel

        print("validated_data['cover'] -> ", validated_data['cover'])
        print("instance.cover -> ", instance.cover)
        
        '''
        validated_data['cover'] ->  IMG_20220816_124135_575.jpg
        instance.cover ->

        validated_data['cover'] ->  None
        instance.cover ->  cover/IMG_20220816_124135_575_CvsBKrf.jpg
        '''
        if instance.cover is not None and validated_data['cover'] is None:
            validated_data['cover'] = instance.cover
        #validated_data['cover'] = instance.cover

        print("validated_data['video'] -> ", validated_data['video'])
        return super().update(instance, validated_data)


class VideoPostEditSerializer(serializers.ModelSerializer):
    word_count = serializers.SerializerMethodField(read_only=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if ('request' in self.context 
            and self.context['request'].user.is_authenticated 
            and self.context['request'].user.is_verified
            and self.context['request'].user.is_staff 
            and self.context['request'].user.is_supervisor == False
            and self.context['request'].user.is_superuser == False):
            read_only_fields_video_for_staff__ = read_only_fields_video_for_staff.copy()
            read_only_fields_video_for_staff__.append('video')
            #read_only_fields_video_for_staff__.append('cover')
            self.Meta.read_only_fields = read_only_fields_video_for_staff__
            
        elif ('request' in self.context 
            and self.context['request'].user.is_authenticated 
            and self.context['request'].user.is_verified
            and (self.context['request'].user.is_supervisor or self.context['request'].user.is_superuser)):
            read_only_fields_video_for_supervisor_or_superuser__ = read_only_fields_video_for_supervisor_or_superuser.copy()
            read_only_fields_video_for_supervisor_or_superuser__.append('video')
            #read_only_fields_video_for_supervisor_or_superuser__.append('cover')
            self.Meta.read_only_fields = read_only_fields_video_for_supervisor_or_superuser__

        else:
            self.Meta.read_only_fields = read_only_fields_video_for_else
    
    class Meta:
        model = VideoPost
        fields = all_fields_video
       
    def validate_tags(self, value):
        if len(value) > 3:
            raise serializers.ValidationError("The number of tags should not exceed 3.")
        return value

    def to_representation(self,instance):
        request = self.context.get('request')
        rep = super().to_representation(instance)
        # when call a serializer into another serializer should also pass the request
        rep['channel'] = ChannelSerializer(instance.channel, context={'request':request}).data
        rep['publisher'] = ProfileSerializer(instance.publisher, context={'request':request}).data
        if instance.video:
            rep['video'] = instance.video.url.split('/media/', 1)[-1]
            rep['video'] = 'media/' + rep['video']
        if instance.cover:
            rep['cover'] = instance.cover.url.split('/media/', 1)[-1]
            rep['cover'] = 'media/' + rep['cover']
        rep['language_video'] = LanguageSerializer(instance.language_video, context={'request':request}).data
        rep['categorys'] = CategorySerializer(instance.categorys, context={'request':request}).data
        rep['sub_categorys'] = CategorySerializer(instance.sub_categorys, context={'request':request}).data
        rep['sub_sub_categorys'] = CategorySerializer(instance.sub_sub_categorys, context={'request':request}).data
        rep['tags'] = TagSerializer(instance.tags.all(), context={'request':request}, many=True).data
        rep['supervisor_to_confirm'] = ProfileSerializer(instance.supervisor_to_confirm, context={'request':request}).data
        return rep
    
    def get_word_count(self, obj):
        return len(obj.description.split(' '))
    
    def create(self,validated_data):
        request = self.context.get('request')
        user = request.user.profile  # Assuming user has a profile

        channel = validated_data['channel']
        is_admin = AdminsOfChannel.objects.filter(channel=channel, admin=user).exists()
        if not (is_admin or user == channel.owner  or request.user.is_supervisor):
            raise PermissionDenied("You cannot post to a channel that you are not the owner or admin of.")
        
        validated_data['publisher'] = user

        if ('request' in self.context 
            and self.context['request'].user.is_authenticated 
            and self.context['request'].user.is_verified
            and self.context['request'].user.is_supervisor):
            validated_data['confirm_to_post'] = True
            validated_data['supervisor_to_confirm'] = Profile.objects.get(user__id=user.id)

        return super().create(validated_data)
    
    # def validate(self, data):
    #     publisher = data['publisher']
    #     channel = data['channel']
    #     if channel.admins.filter(id=publisher.id).exists():
    #         pass
    #     elif publisher == channel.owner:
    #         pass
    #     else:
    #         raise serializers.ValidationError("You cannot post to a channel that you are not the owner or admin of.")
    #     return data

    
    def update(self, instance, validated_data):
        # Fields you want to keep their previous value
        instance.slog = validated_data.get('slog', instance.slog)
        instance.title = validated_data.get('title', instance.title)
        instance.snippet = validated_data.get('snippet', instance.snippet)
        instance.description = validated_data.get('description', instance.description)
        instance.reference = validated_data.get('reference', instance.reference)
        instance.cast = validated_data.get('cast', instance.cast)
        instance.categorys = validated_data.get('categorys', instance.categorys)
        instance.confirm_to_post = validated_data.get('confirm_to_post', instance.confirm_to_post)
        instance.supervisor_to_confirm = validated_data.get('supervisor_to_confirm', instance.supervisor_to_confirm)

        instance.save()
        if 'tags' in validated_data:
            instance.tags.set(validated_data.get('tags'))

        return instance
        

    def update(self, instance, validated_data):
        validated_data['video'] = instance.video
        validated_data['channel'] = instance.channel

        #print("validated_data['cover'] -> ", validated_data['cover'])
        #print("instance.cover -> ", instance.cover)
        
        '''
        validated_data['cover'] ->  IMG_20220816_124135_575.jpg
        instance.cover ->

        
        validated_data['cover'] ->  None
        instance.cover ->  cover/IMG_20220816_124135_575_CvsBKrf.jpg

        '''
        if instance.cover is not None and validated_data['cover'] is None:
        #if validated_data['cover'] is None:
            validated_data['cover'] = instance.cover
        validated_data['cover'] = instance.cover

        # print("validated_data['video'] -> ", validated_data['video'])
        return super().update(instance, validated_data)


class VideoPostEditBodySerializer(serializers.ModelSerializer):
    word_count = serializers.SerializerMethodField(read_only=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if ('request' in self.context 
            and self.context['request'].user.is_authenticated 
            and self.context['request'].user.is_verified
            and self.context['request'].user.is_staff 
            and self.context['request'].user.is_supervisor == False
            and self.context['request'].user.is_superuser == False):
            read_only_fields_video_for_staff__ = read_only_fields_video_for_staff.copy()
            read_only_fields_video_for_staff__.append('video')
            read_only_fields_video_for_staff__.append('cover')
            self.Meta.read_only_fields = read_only_fields_video_for_staff__
            
        elif ('request' in self.context 
            and self.context['request'].user.is_authenticated 
            and self.context['request'].user.is_verified
            and (self.context['request'].user.is_supervisor or self.context['request'].user.is_superuser)):
            read_only_fields_video_for_supervisor_or_superuser__ = read_only_fields_video_for_supervisor_or_superuser.copy()
            read_only_fields_video_for_supervisor_or_superuser__.append('video')
            read_only_fields_video_for_supervisor_or_superuser__.append('cover')
            self.Meta.read_only_fields = read_only_fields_video_for_supervisor_or_superuser__
            
        else:
            self.Meta.read_only_fields = read_only_fields_video_for_else
    
    class Meta:
        model = VideoPost
        fields = all_fields_video
       
    def validate_tags(self, value):
        if len(value) > 3:
            raise serializers.ValidationError("The number of tags should not exceed 3.")
        return value

    def to_representation(self,instance):
        request = self.context.get('request')
        rep = super().to_representation(instance)
        # when call a serializer into another serializer should also pass the request
        rep['channel'] = ChannelSerializer(instance.channel, context={'request':request}).data
        rep['publisher'] = ProfileSerializer(instance.publisher, context={'request':request}).data
        if instance.video:
            rep['video'] = instance.video.url.split('/media/', 1)[-1]
            rep['video'] = 'media/' + rep['video']
        if instance.cover:
            rep['cover'] = instance.cover.url.split('/media/', 1)[-1]
            rep['cover'] = 'media/' + rep['cover']
        rep['language_video'] = LanguageSerializer(instance.language_video, context={'request':request}).data
        rep['categorys'] = CategorySerializer(instance.categorys, context={'request':request}).data
        rep['sub_categorys'] = CategorySerializer(instance.sub_categorys, context={'request':request}).data
        rep['sub_sub_categorys'] = CategorySerializer(instance.sub_sub_categorys, context={'request':request}).data
        rep['tags'] = TagSerializer(instance.tags.all(), context={'request':request}, many=True).data
        rep['supervisor_to_confirm'] = ProfileSerializer(instance.supervisor_to_confirm, context={'request':request}).data
        return rep
    
    def get_word_count(self, obj):
        return len(obj.description.split(' '))
    
    def create(self,validated_data):
        request = self.context.get('request')
        user = request.user.profile  # Assuming user has a profile

        channel = validated_data['channel']
        is_admin = AdminsOfChannel.objects.filter(channel=channel, admin=user).exists()
        if not (is_admin or user == channel.owner  or request.user.is_supervisor):
            raise PermissionDenied("You cannot post to a channel that you are not the owner or admin of.")
        
        validated_data['publisher'] = user

        if ('request' in self.context 
            and self.context['request'].user.is_authenticated 
            and self.context['request'].user.is_verified
            and self.context['request'].user.is_supervisor):
            validated_data['confirm_to_post'] = True
            validated_data['supervisor_to_confirm'] = Profile.objects.get(user__id=user.id)

        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # Fields you want to keep their previous value
        instance.slog = validated_data.get('slog', instance.slog)
        instance.title = validated_data.get('title', instance.title)
        instance.snippet = validated_data.get('snippet', instance.snippet)
        instance.description = validated_data.get('description', instance.description)
        instance.reference = validated_data.get('reference', instance.reference)
        instance.cast = validated_data.get('cast', instance.cast)
        instance.categorys = validated_data.get('categorys', instance.categorys)
        instance.confirm_to_post = validated_data.get('confirm_to_post', instance.confirm_to_post)
        instance.supervisor_to_confirm = validated_data.get('supervisor_to_confirm', instance.supervisor_to_confirm)

        instance.save()
        if 'tags' in validated_data:
            instance.tags.set(validated_data.get('tags'))

        return instance
        

class VideoPostEditCoverSerializer(serializers.ModelSerializer):
    word_count = serializers.SerializerMethodField(read_only=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if ('request' in self.context 
            and self.context['request'].user.is_authenticated 
            and self.context['request'].user.is_verified
            and self.context['request'].user.is_staff 
            and self.context['request'].user.is_supervisor == False
            and self.context['request'].user.is_superuser == False):
            
            self.Meta.read_only_fields = ['id', 'channel', 'publisher', 'slog', 'video', 'hls_master_playlist', 
                  'language_video', 'title', 'snippet', 'meta_description', #'cover',
                  'description', 'reference', 'cast', 'categorys', 'tags', 
                  'counted_views', 'counted_like', 'counted_dislike', 'counted_save', 
                  'counted_share', 'status', 'confirm_to_post', 'supervisor_to_confirm', 
                  'is_pined', 'supervisor_to_pined', 'duration', 
                  'created_date', 'updated_date', 'published_date',]
            
        elif ('request' in self.context 
            and self.context['request'].user.is_authenticated 
            and self.context['request'].user.is_verified
            and (self.context['request'].user.is_supervisor or self.context['request'].user.is_superuser)):
            self.Meta.read_only_fields = ['id', 'channel', 'publisher', 'slog', 'video', 'hls_master_playlist', 
                  'language_video', 'title', 'snippet', 'meta_description', #'cover',
                  'description', 'reference', 'cast', 'categorys', 'tags', 
                  'counted_views', 'counted_like', 'counted_dislike', 'counted_save', 
                  'counted_share', 'status', 'confirm_to_post', 'supervisor_to_confirm', 
                  'is_pined', 'supervisor_to_pined', 'duration', 
                  'created_date', 'updated_date', 'published_date',]

        else:
            self.Meta.read_only_fields = read_only_fields_video_for_else
    
    class Meta:
        model = VideoPost
        fields = all_fields_video
       
    def to_representation(self,instance):
        request = self.context.get('request')
        rep = super().to_representation(instance)
        # when call a serializer into another serializer should also pass the request
        rep['channel'] = ChannelSerializer(instance.channel, context={'request':request}).data
        rep['publisher'] = ProfileSerializer(instance.publisher, context={'request':request}).data
        if instance.video:
            rep['video'] = instance.video.url.split('/media/', 1)[-1]
            rep['video'] = 'media/' + rep['video']
        if instance.cover:
            rep['cover'] = instance.cover.url.split('/media/', 1)[-1]
            rep['cover'] = 'media/' + rep['cover']
        rep['language_video'] = LanguageSerializer(instance.language_video, context={'request':request}).data
        rep['categorys'] = CategorySerializer(instance.categorys, context={'request':request}).data
        rep['sub_categorys'] = CategorySerializer(instance.sub_categorys, context={'request':request}).data
        rep['sub_sub_categorys'] = CategorySerializer(instance.sub_sub_categorys, context={'request':request}).data
        rep['tags'] = TagSerializer(instance.tags.all(), context={'request':request}, many=True).data
        rep['supervisor_to_confirm'] = ProfileSerializer(instance.supervisor_to_confirm, context={'request':request}).data
        return rep
    
    def get_word_count(self, obj):
        return len(obj.description.split(' '))
    

class VideoPostEditVideoSerializer(serializers.ModelSerializer):
    word_count = serializers.SerializerMethodField(read_only=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if ('request' in self.context 
            and self.context['request'].user.is_authenticated 
            and self.context['request'].user.is_verified
            and self.context['request'].user.is_staff 
            and self.context['request'].user.is_supervisor == False
            and self.context['request'].user.is_superuser == False):
            
            self.Meta.read_only_fields = ['id', 'channel', 'publisher', 'slog', 'hls_master_playlist', 
                  'language_video', 'title', 'snippet', 'meta_description', 'cover',
                  'description', 'reference', 'cast', 'categorys', 'tags', 
                  'counted_views', 'counted_like', 'counted_dislike', 'counted_save', 
                  'counted_share', 'status', 'confirm_to_post', 'supervisor_to_confirm', 
                  'is_pined', 'supervisor_to_pined', 'duration', 
                  'created_date', 'updated_date', 'published_date', ]
            
        elif ('request' in self.context 
            and self.context['request'].user.is_authenticated 
            and self.context['request'].user.is_verified
            and (self.context['request'].user.is_supervisor or self.context['request'].user.is_superuser)):
            self.Meta.read_only_fields = ['id', 'channel', 'publisher', 'slog', 'hls_master_playlist', 
                  'language_video', 'title', 'snippet', 'meta_description', 'cover',
                  'description', 'reference', 'cast', 'categorys', 'tags', 
                  'counted_views', 'counted_like', 'counted_dislike', 'counted_save', 
                  'counted_share', 'status', 'confirm_to_post', 'supervisor_to_confirm', 
                  'is_pined', 'supervisor_to_pined', 'duration', 
                  'created_date', 'updated_date', 'published_date', ]

        else:
            self.Meta.read_only_fields = read_only_fields_video_for_else
    
    class Meta:
        model = VideoPost
        fields = all_fields_video
       
    
    def to_representation(self,instance):
        request = self.context.get('request')
        rep = super().to_representation(instance)
        # when call a serializer into another serializer should also pass the request
        rep['channel'] = ChannelSerializer(instance.channel, context={'request':request}).data
        rep['publisher'] = ProfileSerializer(instance.publisher, context={'request':request}).data
        if instance.video:
            rep['video'] = instance.video.url.split('/media/', 1)[-1]
            rep['video'] = 'media/' + rep['video']
        if instance.cover:
            rep['cover'] = instance.cover.url.split('/media/', 1)[-1]
            rep['cover'] = 'media/' + rep['cover']
        rep['language_video'] = LanguageSerializer(instance.language_video, context={'request':request}).data
        rep['categorys'] = CategorySerializer(instance.categorys, context={'request':request}).data
        rep['sub_categorys'] = CategorySerializer(instance.sub_categorys, context={'request':request}).data
        rep['sub_sub_categorys'] = CategorySerializer(instance.sub_sub_categorys, context={'request':request}).data
        rep['tags'] = TagSerializer(instance.tags.all(), context={'request':request}, many=True).data
        rep['supervisor_to_confirm'] = ProfileSerializer(instance.supervisor_to_confirm, context={'request':request}).data
        return rep

        
    def get_word_count(self, obj):
        return len(obj.description.split(' '))
############################################################################################################    


class SubCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'comment', 'user', 'created_date']

class CommentSerializer(serializers.ModelSerializer):
    sub_comments = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        '''
        if ('request' in self.context 
            and self.context['request'].user.is_authenticated 
            and self.context['request'].user.is_verified
            #and self.context['request'].user.is_staff == False
            and self.context['request'].user.is_supervisor == False
            and self.context['request'].user.is_superuser == False):
            self.Meta.read_only_fields = ['id', 'user', 'confirm_to_comment', 'supervisor_to_confirm',
                  'created_date', 'updated_date',]
        '''
        # supervisor & superuser
        if ('request' in self.context 
            and self.context['request'].user.is_authenticated 
            and self.context['request'].user.is_verified
            and self.context['request'].user.is_staff 
            and self.context['request'].user.is_supervisor
            and self.context['request'].user.is_superuser):
            self.Meta.read_only_fields = ['id', 'user',
                  'created_date', 'updated_date',]
        
        # staff
        elif ('request' in self.context 
            and self.context['request'].user.is_authenticated 
            and self.context['request'].user.is_verified
            and self.context['request'].user.is_staff
            and self.context['request'].user.is_supervisor == False
            and self.context['request'].user.is_superuser == False):
            self.Meta.read_only_fields = ['id', 'user', 'confirm_to_comment', 'supervisor_to_confirm',
                  'created_date', 'updated_date',]
        
        # nobody
        elif ('request' in self.context 
            and self.context['request'].user.is_authenticated 
            #and self.context['request'].user.is_verified == False
            and self.context['request'].user.is_staff == False
            and self.context['request'].user.is_supervisor == False
            and self.context['request'].user.is_superuser == False
            ):
            self.Meta.read_only_fields = ['id', 'user', 
                  'confirm_to_comment', 'supervisor_to_confirm',
                  'created_date', 'updated_date', ]
            
        # not login
        elif ('request' in self.context 
            and self.context['request'].user.is_authenticated == False
            #and self.context['request'].user.is_verified == False
            #and self.context['request'].user.is_staff == False
            #and self.context['request'].user.is_supervisor == False
            #and self.context['request'].user.is_superuser == False
            ):
            self.Meta.read_only_fields = ['id', 'video_post', 'uper_comment', 'user', 'comment', 
                  'confirm_to_comment', 'supervisor_to_confirm',
                  'created_date', 'updated_date', ]

    def get_sub_comments(self, obj):
        view = self.context.get('view')
        
        if view is not None and hasattr(view, 'action') and view.action == 'retrieve':
            sub_comments = Comment.objects.filter(uper_comment=obj, confirm_to_comment=True)
            return SubCommentSerializer(sub_comments, many=True).data
        
        return None

    class Meta:
        model = Comment
        fields = ['id', 'video_post', 'uper_comment', 'user', 'comment', 
                  'confirm_to_comment', 'supervisor_to_confirm',
                  'created_date', 'updated_date', 'sub_comments',]
    
    def to_representation(self,instance):
        request = self.context.get('request')
        rep = super().to_representation(instance)
        rep['user'] = ProfileSerializer(instance.user, context={'request':request}).data
        rep['supervisor_to_confirm'] = ProfileSerializer(instance.supervisor_to_confirm, context={'request':request}).data
        rep['video_post'] = VideoPostSerializer(instance.video_post, context={'request':request}).data
        rep['uper_comment'] = CommentSerializer(instance.uper_comment, context={'request':request}).data
        
        view = self.context.get('view')
        if view and hasattr(view, 'action') and view.action == 'retrieve':
            # Only include sub_comments in detail view (retrieve action)
            rep['sub_comments'] = self.get_sub_comments(instance)
        else:
            # Do not include sub_comments in list view
            rep['sub_comments'] = None
        
        return rep

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        validated_data['user'] = request.user.profile

        video_post = validated_data.get('video_post')
        if not video_post:
            with open('comments_log.txt', 'a') as file:
                file.write(str(validated_data))
                file.write('\n')
                
            raise serializers.ValidationError("Video post is required.")
    
        video_post = validated_data.get('video_post')

        if ('request' in self.context 
            and self.context['request'].user.is_authenticated 
            and self.context['request'].user.is_verified
            and self.context['request'].user.is_supervisor):
            validated_data['confirm_to_comment'] = True
            validated_data['supervisor_to_confirm'] = Profile.objects.get(user__id=user.id)

        return super().create(validated_data)

    def validate(self, data):

        if data.get('uper_comment') : # if data['uper_comment']:
            uper_comment = data['uper_comment']
            uper_comment_post = uper_comment.video_post
            choise_video_post = data['video_post']
            if choise_video_post != uper_comment_post:
                raise serializers.ValidationError("You cannot reply to another comment in another post.")
        return data


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'video_post',]
        read_only_fields = ['user']

    def to_representation(self,instance):
        request = self.context.get('request')
        rep = super().to_representation(instance)

        # when call a serializer into another serializer should also pass the request
        rep['user'] = ProfileSerializer(instance.user, context={'request':request}).data
        rep['video_post'] = VideoPostSerializer(instance.video_post, context={'request':request}).data
        return rep

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['user'] = request.user.profile
        return super().create(validated_data)


class DisLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dislike
        fields = ['id', 'user', 'video_post',]
        read_only_fields = ['user']

    def to_representation(self,instance):
        request = self.context.get('request')
        rep = super().to_representation(instance)

        # when call a serializer into another serializer should also pass the request
        rep['user'] = ProfileSerializer(instance.user, context={'request':request}).data
        rep['video_post'] = VideoPostSerializer(instance.video_post, context={'request':request}).data
        return rep

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['user'] = request.user.profile
        return super().create(validated_data)


class SaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Save
        fields = ['id', 'user', 'video_post',]
        read_only_fields = ['user']

    def to_representation(self,instance):
        request = self.context.get('request')
        rep = super().to_representation(instance)

        # when call a serializer into another serializer should also pass the request
        rep['user'] = ProfileSerializer(instance.user, context={'request':request}).data
        rep['video_post'] = VideoPostSerializer(instance.video_post, context={'request':request}).data
        return rep

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['user'] = request.user.profile
        return super().create(validated_data)


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


class PlayListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayList
        fields = ['id', 'channel', 'creator', 'package_name', 'package_description', 
                  'play_list_videos', 'created_date', 'updated_date']

    def to_representation(self,instance):
        request = self.context.get('request')
        rep = super().to_representation(instance)

        # when call a serializer into another serializer should also pass the request
        rep['channel'] = ChannelSerializer(instance.channel, context={'request':request}).data
        rep['creator'] = ProfileSerializer(instance.creator, context={'request':request}).data
        rep['play_list_videos'] = VideoPostSerializer(instance.play_list_videos.all(), context={'request':request}, many=True).data
        return rep

    def validate(self, data):
        channel = data.get('channel')
        creator = data.get('creator')
        play_list_videos = data.get('play_list_videos')

        for video in play_list_videos:
            if video.channel != channel:
                raise ValidationError("The channel of the videos in the playlist must match the channel of the playlist")
        
        # We assume that channel is a ForeignKey relation to the Channel model
        if not (creator == channel.owner or creator in channel.admins.all()):
            raise ValidationError("Creator must be the owner or one of the channel admins.")
        
        return data

    def create(self, validated_data):
        play_list_videos = validated_data.pop('play_list_videos', None)
        play_list = PlayList.objects.create(**validated_data)
        
        if play_list_videos:
            play_list.play_list_videos.set(play_list_videos)
        
        return play_list
    

class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = ['id', 'user', 'video', 'timestamp', 'percentage_watched', 'last_viewed']
        read_only_fields = ['last_viewed', 'user']

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['user'] = request.user.profile
        return super().create(validated_data)

    def to_representation(self,instance):
        request = self.context.get('request')
        rep = super().to_representation(instance)
        # when call a serializer into another serializer should also pass the request
        rep['user'] = ProfileSerializer(instance.user, context={'request':request}).data
        rep['video'] = VideoPostSerializer(instance.video, context={'request':request}).data
        return rep


class SpecialSectionSerializer(serializers.ModelSerializer):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if ('request' in self.context 
            and self.context['request'].user.is_authenticated 
            and self.context['request'].user.is_verified
            and self.context['request'].user.is_staff 
            and self.context['request'].user.is_supervisor == False
            and self.context['request'].user.is_superuser == False):
            self.Meta.read_only_fields = ['id', 'creator', 'section_name', 'special_item', #'is_active', 
                  'created_date', 'updated_date']
            
        elif ('request' in self.context 
            and self.context['request'].user.is_authenticated 
            and self.context['request'].user.is_verified
            and (self.context['request'].user.is_supervisor or self.context['request'].user.is_superuser)):
            self.Meta.read_only_fields = ['creator']

        else:
            self.Meta.read_only_fields = ['id', 'creator', 'section_name', 'special_item', #'is_active', 
                                'created_date', 'updated_date']
    
    class Meta:
        model = SpecialSection
        fields = ['id', 'special_item', 'section_name', #'is_active', 
                  'created_date', 'updated_date']
        read_only_fields = ['creator']

    def to_representation(self,instance):
        request = self.context.get('request')
        rep = super().to_representation(instance)

        # when call a serializer into another serializer should also pass the request
        rep['creator'] = ProfileSerializer(instance.creator, context={'request':request}).data
        rep['special_item'] = VideoPostSerializer(instance.special_item, context={'request':request}).data
        #rep['special_item'] = VideoPostSerializer(instance.special_item.all(), context={'request':request}, many=True).data
        return rep

    def create(self,validated_data):
        request = self.context.get('request')
        user = request.user.profile  # Assuming user has a profile
        validated_data['creator'] = user

        if 'section_name' not in validated_data:
            raise PermissionDenied("You cannot set SpecialSection")

        return super().create(validated_data)


class AdminsOfChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminsOfChannel
        fields = '__all__'
        read_only_fields = ('user_adder',)

    def to_representation(self,instance):
        request = self.context.get('request')
        rep = super().to_representation(instance)

        # when call a serializer into another serializer should also pass the request
        rep['user_adder'] = ProfileSerializer(instance.user_adder, context={'request':request}).data
        rep['channel'] = ChannelSerializer(instance.channel, context={'request':request}).data
        rep['admin'] = ProfileSerializer(instance.admin, context={'request':request}).data

        return rep


class SocialOfChanneSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialOfChanne
        fields = '__all__'
        read_only_fields = ('user_adder',)
    
    def to_representation(self,instance):
        request = self.context.get('request')
        rep = super().to_representation(instance)

        # when call a serializer into another serializer should also pass the request
        rep['user_adder'] = ProfileSerializer(instance.user_adder, context={'request':request}).data
        rep['channel'] = ChannelSerializer(instance.channel, context={'request':request}).data

        return rep




class ChannelSerializer__(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = [
            'id', 'avatar', 'banner', 'owner', 'name', 'categorys',
            'handle', 'description', 'subscribe_count', 'counted_view',
            'activation', 'is_favorite', 
            'supervisor_to_favorited', 'supervisor_to_confirm', 
            'confirm_to_channel', 'created_date', 'updated_date'
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        rep = super().to_representation(instance)
        rep['owner'] = ProfileSerializer(instance.owner, context={'request': request}).data
        rep['categorys'] = CategorySerializer(instance.categorys, context={'request':request}).data
        rep['supervisor_to_favorited'] = ProfileSerializer(instance.supervisor_to_favorited, context={'request': request}).data
        rep['supervisor_to_confirm'] = ProfileSerializer(instance.supervisor_to_confirm, context={'request': request}).data
        return rep
    
class TagSerializer__(serializers.ModelSerializer):
    
    class Meta:
        model = Tag
        fields = ['id', 'name', 'confirm']

class VideoPostSerializer__(serializers.ModelSerializer):
    word_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = VideoPost
        fields = all_fields_video
       
    def to_representation(self,instance):
        request = self.context.get('request')
        rep = super().to_representation(instance)
        # when call a serializer into another serializer should also pass the request
        rep['channel'] = ChannelSerializer__(instance.channel, context={'request':request}).data
        rep['publisher'] = ProfileSerializer(instance.publisher, context={'request':request}).data
        rep['language_video'] = LanguageSerializer(instance.language_video, context={'request':request}).data
        rep['categorys'] = CategorySerializer(instance.categorys, context={'request':request}).data
        rep['tags'] = TagSerializer__(instance.tags.all(), context={'request':request}, many=True).data
        rep['supervisor_to_confirm'] = ProfileSerializer(instance.supervisor_to_confirm, context={'request':request}).data
        return rep
    
    def get_word_count(self, obj):
        return len(obj.description.split(' '))
    


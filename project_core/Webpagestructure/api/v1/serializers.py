from Webpagestructure.models import *
from accounts.models import Profile
from rest_framework import serializers, permissions
from rest_framework.exceptions import ValidationError
from channels.api.v1.serializers import VideoPostSerializer, VideoPostSerializer
from attachments.api.v1.serializers import TagSerializer, CategorySerializer

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'first_name', 'last_name', 'image']



class SiteHeaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteHeader
        fields = ['id', 'name', 'logo', 'alternative_logo',] # 'created_date', 'updated_date']
       
    def validate_name(self, value):
        if SiteHeader.objects.filter(name=value).exists():
            raise ValidationError("This name is already used, please choose another name.")
        return value



class LinkSectionInFooterSerializer(serializers.ModelSerializer):
    class Meta:
        model = LinkSection
        fields = ['id', 'name', 'link', 'alternative_link', ]
        


class SocialSectionInFooterSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialSection
        fields = ['id', 'name', 'link', 'alternative_link', 'logo', 'alternative_logo',]
        


class SiteFooterSerializer(serializers.ModelSerializer): 
    class Meta:
        model = SiteFooter
        fields = ['id', 'links_section', 'social_section', 'legal_sentence_of_right_of_ownership', 
                  'link_of_right_of_ownership_site', ]
    
    def to_representation(self,instance):
        request = self.context.get('request')
        rep = super().to_representation(instance)

        rep['links_section'] = LinkSectionInFooterSerializer(instance.links_section.all(), context={'request':request}, many=True).data
        rep['social_section'] = SocialSectionInFooterSerializer(instance.social_section.all(), context={'request':request}, many=True).data
        return rep
    

class SiteThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteTheme
        fields = ['id', 'theme_name', 'black', 'white', 'gray', 'primaryColor', 
                  'secondaryColor', 'gradientFirstColor', 'gradientSecondColor', 'type_theme']
       


class SiteStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteStructure
        fields = ['id', 'site_name', 'header', 'fooer', 'dark_theme', 'light_theme', ]
    
    def to_representation(self,instance):
        request = self.context.get('request')
        rep = super().to_representation(instance)

        rep['header'] = SiteHeaderSerializer(instance.header, context={'request':request}).data
        rep['fooer'] = SiteFooterSerializer(instance.fooer, context={'request':request}).data
        rep['dark_theme'] = SiteThemeSerializer(instance.dark_theme, context={'request':request}).data
        rep['light_theme'] = SiteThemeSerializer(instance.light_theme, context={'request':request}).data
        return rep
    






class BoxManagmentSerializer(serializers.ModelSerializer ):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if ('request' in self.context 
            and self.context['request'].user.is_authenticated 
            and self.context['request'].user.is_verified
            and (self.context['request'].user.is_supervisor or self.context['request'].user.is_superuser)):
            self.Meta.read_only_fields = ['supervisor_to_add', ]
    
        else:
            self.Meta.read_only_fields = ['box_name', 'name_in_view', 'box_location', 'box_priority', 
                                          'content_type', 'categorys', 'sub_categorys', 
                                            'sub_sub_categorys' , 'tags', 'cach_time', 'item_count', 
                                            'box_item_type', 'status', 'supervisor_to_add', 'back_ground_color_code']
    
    class Meta:
        model = BoxManagment
        fields = ['id', 'box_name', 'name_in_view', 'box_location', 'box_priority', 'content_type', 'categorys', 'sub_categorys', 
                  'sub_sub_categorys' , 'tags', 'cach_time', 'item_count', 'box_item_type', 'status',
                  'supervisor_to_add', 'back_ground_color_code', 'updated_date', 'created_date']

    def validate(self, data): #Used to avoid conflicts between "manual" and "automatic" box modes.
        # Check if box_item_type is equal to 'auto'
        if data.get('box_item_type') and data['box_item_type'] == 'auto':
            box = self.instance  # if there is an instance (for the update operation)
            if box:
                # Remove all records associated with this box from ItemsBoxByHand
                ItemsBoxByHand.objects.filter(box=box).delete()
        return data   
    
    def to_representation(self,instance):
        request = self.context.get('request')
        rep = super().to_representation(instance)
        # when call a serializer into another serializer should also pass the request
        rep['box_location'] = LocationBoxSerializer(instance.box_location, context={'request':request}).data
        rep['categorys'] = CategorySerializer(instance.categorys, context={'request':request}).data
        rep['sub_categorys'] = CategorySerializer(instance.sub_categorys, context={'request':request}).data
        rep['sub_sub_categorys'] = CategorySerializer(instance.sub_sub_categorys, context={'request':request}).data
        rep['tags'] = TagSerializer(instance.tags, context={'request':request}).data
        rep['supervisor_to_add'] = ProfileSerializer(instance.supervisor_to_add, context={'request':request}).data
        return rep
    
    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['supervisor_to_add'] = request.user.profile
        if validated_data['supervisor_to_add'].user.is_supervisor:
            return super().create(validated_data)
        else:
            raise serializers.ValidationError("permission denied")
    
    def update(self, instance, validated_data):
        ## print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
        # Check if box_item_type is 'auto'
        if validated_data.get('box_item_type') and validated_data['box_item_type'] == 'atuo':
            # Remove all records associated with this box from ItemsBoxByHand
            ## print("################################\n", validated_data['box_item_type'].name)
            ItemsBoxByHand.objects.filter(box=instance).delete()

        return super().update(instance, validated_data)


class VideoItemsBoxByHandSerializer(serializers.ModelSerializer ):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if ('request' in self.context 
            and self.context['request'].user.is_authenticated 
            and self.context['request'].user.is_verified
            and (self.context['request'].user.is_supervisor or self.context['request'].user.is_superuser)):
            self.Meta.read_only_fields = ['user', ]
    
        else:
            self.Meta.read_only_fields = ['user', 'box', 'video',]
    
    class Meta:
        model = ItemsBoxByHand
        fields = ['id', 'user', 'box', 'video',]

    def validate(self, data):
        box = data.get('box')
        video = data.get('video')

        # Check if both are selected or not
        if box and video:
            if box.content_type != 'video':
                raise serializers.ValidationError('The type of elements allowed in this video box is not.')
            
            # Checking the compatibility of category, subcategory and...
            if box.categorys:
                if box.categorys != video.categorys:
                    raise serializers.ValidationError("The selected video category does not match the box.")
            
            if box.sub_categorys:
                if box.sub_categorys != video.sub_categorys:
                    raise serializers.ValidationError("Subcategory 1 of the selected video does not match the box.")
            
            if box.sub_sub_categorys:
                if box.sub_sub_categorys != video.sub_sub_categorys:
                    raise serializers.ValidationError("2 selected video subcategories do not match the box.")
            
            if box.tags:
                if box.tags and not video.tags.filter(id=box.tags.id).exists():
                    raise serializers.ValidationError("The selected video tag does not match the tagbox.")

            # Count the videos in the box
            current_item_count = box.box.count()
            # Checking the current number of items with the value of item_count in the BoxManagment model
            if current_item_count >= box.item_count:
                raise serializers.ValidationError("The number of items in the box exceeds the limit.")
        
        return data

    def to_representation(self,instance):
        request = self.context.get('request')
        rep = super().to_representation(instance)
        # when call a serializer into another serializer should also pass the request
        rep['box'] = BoxManagmentSerializer(instance.box, context={'request':request}).data
        rep['video'] = VideoPostSerializer(instance.video, context={'request':request}).data
        rep['user'] = ProfileSerializer(instance.user, context={'request':request}).data
        return rep

    def create(self, validated_data):
        box = validated_data.get('box')
        if box.box_item_type and box.box_item_type == 'atuo':
            raise serializers.ValidationError("It is not possible to add items to this box because its type is auto.")

        request = self.context.get('request')
        validated_data['user'] = request.user.profile
        if validated_data['user'].user.is_supervisor:
            return super().create(validated_data)
        else:
            raise serializers.ValidationError("permission denied")
        


class LocationBoxSerializer(serializers.ModelSerializer ):
    class Meta:
        model = LocationBox
        fields = ['id', 'name']


class OfferForBoxFromOwnerChannelSerializer(serializers.ModelSerializer ):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if ('request' in self.context 
            and self.context['request'].user.is_authenticated 
            and self.context['request'].user.is_verified
            and (self.context['request'].user.is_supervisor or self.context['request'].user.is_superuser)):
            self.Meta.read_only_fields = ['supervisor', 'proposing_user']
        
        elif ('request' in self.context 
            and self.context['request'].user.is_authenticated 
            and self.context['request'].user.is_verified
            and self.context['request'].user.is_staff):
            self.Meta.read_only_fields = ['supervisor', 'proposing_user', 'is_accept']
    
        else:
            self.Meta.read_only_fields = ['proposing_user', 'video', 'box', 'is_accept', 'supervisor', ]
    
    class Meta:
        model = OfferForBoxFromOwnerChannel
        fields = ['id', 'proposing_user', 'video', 'box', 'is_accept', 'supervisor', ]
    
    def validate(self, data):
        box = data.get('box')
        video = data.get('video')
        channel = video.channel

        # Counting the number of suggested videos from this channel for this box
        existing_videos_count = OfferForBoxFromOwnerChannel.objects.filter(
            box=box,
            video__channel=channel
        ).count()

        # If it was more than 3, throw an error
        if existing_videos_count >= 3:
            raise serializers.ValidationError("Up to 3 videos from each channel can be suggested to one box.")

        return data

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['proposing_user'] = request.user.profile
        if validated_data.get('is_accept') and request.user.profile.user.is_supervisor:
            validated_data['supervisor'] = request.user.profile

        video = validated_data.get('video')
        if video.channel.owner != validated_data['proposing_user']:
            raise serializers.ValidationError("You must be the owner of the post channel to suggest a video post to the editor")
    
        return super().create(validated_data)
        
    def update(self, instance, validated_data):
        request = self.context.get('request')
        if validated_data['is_accept'] and request.user.profile.user.is_supervisor:
            validated_data['supervisor'] = request.user.profile
        else:
            validated_data['is_accept'] = False
        
        return super().update(instance, validated_data)
    
    def to_representation(self,instance):
        request = self.context.get('request')
        rep = super().to_representation(instance)
        # when call a serializer into another serializer should also pass the request
        rep['proposing_user'] = ProfileSerializer(instance.proposing_user, context={'request':request}).data
        rep['video'] = VideoPostSerializer(instance.video, context={'request':request}).data
        rep['box'] = BoxManagmentSerializer(instance.box, context={'request':request}).data
        rep['supervisor'] = ProfileSerializer(instance.supervisor, context={'request':request}).data
        return rep




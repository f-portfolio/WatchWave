from attachments.models import *
from rest_framework import serializers, permissions
from accounts.api.v1.serializers import *
from channels.models import *
from django.utils import timezone


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'first_name', 'last_name', 'image']



class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'confirm', 'user_adder', 'created_date', 'updated_date']
        read_only_fields = ['user_adder',]
    
    def validate_confirm(self, value):
        user = self.context['request'].user.profile  
        if user:
            today = timezone.now().date()
            confirmed_tags_today = Tag.objects.filter(
                user_adder=user,
                created_date__date=today,
                confirm=True
            ).count()
            
            if confirmed_tags_today >= 5 and value is True:
                raise serializers.ValidationError("You have added more than 5 approved tags today. New tags will not be approved automatically.")
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['user_adder'] = request.user.profile
        if validated_data['user_adder'].user.is_staff == False:
            raise serializers.ValidationError("permission denied")
        
        
        user = self.context['request'].user.profile
        if user:
            today = timezone.now().date()
            confirmed_tags_today = Tag.objects.filter(
                user_adder=user,
                created_date__date=today,
                confirm=True
            ).count()
            if confirmed_tags_today >= 5:
                validated_data['confirm'] = False   

        return super().create(validated_data)
    
    def to_representation(self,instance):
        request = self.context.get('request')
        rep = super().to_representation(instance)
        # when call a serializer into another serializer should also pass the request
        rep['user_adder'] = ProfileSerializer(instance.user_adder, context={'request':request}).data
        return rep

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['id', 'name']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'type']


class URLSerializer(serializers.ModelSerializer): 
    class Meta:
        model = URL
        fields = ['id', 'name', 'alternative', 'url', 'caption', 'type', 'added_at', ]


class TypeOfURLSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeOfURL
        fields = ['id', 'name',]


class TypeOfAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeOfAuthor
        fields = ['id', 'name',]


class LinkOfPostsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LinkOfPosts
        fields = ['id', 'name', 'address', 'added_at']


class MetaKwordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetaKword
        fields = ['id', 'name']


class ContentTypeBoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentType
        fields = ['id', 'name']


class TagCategorySerializer(serializers.Serializer):
    tag_id = serializers.IntegerField()
    tag_name = serializers.CharField()
    category_id = serializers.IntegerField(allow_null=True)
    category_name = serializers.CharField(allow_null=True)
    sub_category_id = serializers.IntegerField(allow_null=True)
    sub_category_name = serializers.CharField(allow_null=True)
    sub_sub_category_id = serializers.IntegerField(allow_null=True)
    sub_sub_category_name = serializers.CharField(allow_null=True)








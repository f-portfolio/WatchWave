import re, redis, hashlib
from accounts.models import User, Profile, PromotionRequest
from django.core import exceptions
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers


redis_cli = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)


class RegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, required=True )

    class Meta:
        model = User
        fields = ('username', 'password', 'confirm_password')
        extra_kwargs = {
            'password': {
                'write_only': True,
                # 'style': {'input_type': 'password'}
                },
        }

    def validate_username(self, username):
        """
        Validates if the username is either a valid phone number or a valid email address.
        """
        phone_number_pattern = r'^09\d{9}$'  # Regular expression pattern for phone numbers (11 digits)
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'  # Improved email pattern

        # Check if username matches phone number format
        if re.match(phone_number_pattern, username):
            return username  # Valid phone number

        # Check if username matches email format
        elif re.match(email_pattern, username):
            return username  # Valid email address

        # If not a valid phone number or email, raise an error
        raise serializers.ValidationError('Username must be either a valid phone number (starting with 09 and 11 digits)or a valid email address.')
        
        # You can remove the return statement at the end as it's unreachable
        # due to the raised exception if neither format matches.
            
    def validate(self, data):
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if password != confirm_password:
            raise serializers.ValidationError('Passwords do not match.')

        return data

    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user

class ConfirmRegistrationSerializer(serializers.Serializer):
    code = serializers.CharField(required=True)

    def validate_code(self, code):
        user = self.context.get('user')  # Access user object from context

        # Validate code presence and user validity
        if not code:
            raise serializers.ValidationError('Code is required.')
        if not user:
            raise serializers.ValidationError('Invalid user.')

        # Retrieve confirmation code from Redis
        stored_code = redis_cli.get(user.username)

        # Hash the entered code for comparison
        entered_code_hash = hashlib.sha256(code.encode('utf-8')).hexdigest()

        # Validate code match and expiration
        if not stored_code:
            raise serializers.ValidationError('Confirmation code not found.')
        if str(stored_code) != str(entered_code_hash):
            raise serializers.ValidationError('Invalid confirmation code.')

        # Mark user as verified
        user.is_verified = True
        user.save()

        return code  # Return validated code
    

User = get_user_model()

class PasswordResetRequestSerializer(serializers.Serializer):
    code = serializers.CharField(required=True)
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = self.context.get('user')  # Access user object from context

        # Validate code presence and user validity
        if not data['code']:
            raise serializers.ValidationError('Code is required.')
        if not user:
            raise serializers.ValidationError('Invalid user.')

        # Retrieve confirmation code from Redis
        stored_code = redis_cli.get(user.username)

        # Hash the entered code for comparison
        entered_code_hash = hashlib.sha256(data['code'].encode('utf-8')).hexdigest()

        # Validate code match and expiration
        if not stored_code:
            raise serializers.ValidationError('Confirmation code not found.')
        if str(stored_code) != str(entered_code_hash):
            raise serializers.ValidationError('Invalid confirmation code.')

        # Mark user as verified
        user.set_password(data['new_password'])
        user.save()
        return data  # Return validated code


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    uidb64 = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            uid = force_str(urlsafe_base64_decode(data['uidb64']))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError('Invalid token or user ID')
        
        if not PasswordResetTokenGenerator().check_token(user, data['token']):
            raise serializers.ValidationError('Invalid token or user ID')

        return data

    def save(self, validated_data):
        uid = force_str(urlsafe_base64_decode(validated_data['uidb64']))
        user = User.objects.get(pk=uid)
        user.set_password(validated_data['new_password'])
        user.save()
        return user
    

class TokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(self, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        if user.is_superuser and user.is_supervisor and user.is_staff:
            role = 'is_superuser'
        elif not user.is_superuser and user.is_supervisor and user.is_staff:
            role = 'is_supervisor'
        elif not user.is_superuser and not user.is_supervisor and user.is_staff :
            role = 'staff'
        else :
            role = 'nobody'
        token['role'] = role

        if user.is_verified:
            token['verified'] = True
        else:
            token['verified'] = False

        # Add permissions to the token
        if user.group_permissions:
            permissions = user.group_permissions.permissions.all().values_list('name', flat=True)
            token['permissions'] = list(permissions)
        else:
            token['permissions'] = []

        return token
    
    def validate(self, attrs):
        validated_data = super().validate(attrs)
        validated_data['user_id'] = self.user.id
        validated_data['username'] = self.user.username
        if self.user.is_superuser and self.user.is_supervisor and self.user.is_staff:
            role = 'is_superuser'
        elif not self.user.is_superuser and self.user.is_supervisor and self.user.is_staff:
            role = 'is_supervisor'
        elif not self.user.is_superuser and not self.user.is_supervisor and self.user.is_staff :
            role = 'staff'
        else :
            role = 'nobody'
        validated_data['role']= role
        validated_data['message']= 'Login successful'
        
        if self.user.is_verified:
            validated_data['verified'] = True
        else:
            validated_data['verified'] = False
        
         # Add permissions to the response
        if self.user.group_permissions:
            permissions = self.user.group_permissions.permissions.all().values_list('name', flat=True)
            validated_data['permissions'] = list(permissions)
        else:
            validated_data['permissions'] = []

        return validated_data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username',]


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    class Meta:
        model = Profile
        fields = ['id', 'user', 'first_name', 'last_name', 'image', 'description', 'sex',
                'province', 'city', 'job', 'education', 'created_date', 'updated_date']

    def to_representation(self,instance):
        request = self.context.get('request')
        rep = super().to_representation(instance)
        # when call a serializer into another serializer should also pass the request
        if instance.image:
            rep['image'] = instance.image.url.split('/media/', 1)[-1]
            rep['image'] = 'media/' + rep['image']
        return rep
        
class ProfileEditBodySerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    class Meta:
        model = Profile
        fields = ['id', 'user', 'first_name', 'last_name', 'description', 'sex',
                'province', 'city', 'job', 'education', 'created_date', 'updated_date']
        
    def to_representation(self,instance):
        request = self.context.get('request')
        rep = super().to_representation(instance)
        # when call a serializer into another serializer should also pass the request
        ##@ rep['image'] = instance.image.url 
        if instance.image:
            rep['image'] = instance.image.url.split('/media/', 1)[-1]
            rep['image'] = 'media/' + rep['image']
        return rep
    
class ProfileEditImageSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Profile
        fields = ['user', 'image', ]
        read_only_fields = ['id', 'user', 'first_name', 'last_name', 'description', 'sex',
                'province', 'city', 'job', 'education', 'created_date', 'updated_date']
    def update(self, instance, validated_data):
        # Check and update banner only if it's not None
        if validated_data.get('image') is not None:
            instance.image = validated_data.get('image', instance.image)
        # Save and return the updated instance
        instance.save()
        return instance
    
    def update(self, instance, validated_data):
        if validated_data['image'] is None:
            validated_data['image'] = instance.image
        return super().update(instance, validated_data)

    def to_representation(self,instance):
        request = self.context.get('request')
        rep = super().to_representation(instance)
        # when call a serializer into another serializer should also pass the request
        ##@ rep['image'] = instance.image.url 
        if instance.image:
            rep['image'] = instance.image.url.split('/media/', 1)[-1]
            rep['image'] = 'media/' + rep['image']
        return rep
    
class ChangePasswordSerialier(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password1 = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs.get('new_password') != attrs.get('new_password1'):
            raise serializers.ValidationError({'detail': 'passswords doesnt match'})
        try:
            validate_password(attrs.get('new_password'))
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({'new_password': list(e.messages)})
        return super().validate(attrs)
    
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(
        label=_("username"),
        write_only=True
    )
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    token = serializers.CharField(
        label=_("Token"),
        read_only=True
    )
    
class ObtainTokenSerializer(serializers.Serializer):
    token =serializers.CharField(max_length=128 , allow_null=False)
    refresh =serializers.CharField(max_length=128 , allow_null=False)
    created = serializers.BooleanField()


class TokenSerializer(serializers.Serializer):
    token = serializers.CharField()


class PromotionRequestSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if ('request' in self.context 
            and self.context['request'].user.is_authenticated 
            and self.context['request'].user.is_verified
            and self.context['request'].user.is_staff == False
            and self.context['request'].user.is_supervisor == False
            and self.context['request'].user.is_superuser == False):
            self.Meta.read_only_fields = ['user', 'is_approved', ]
            
        elif ('request' in self.context 
            and self.context['request'].user.is_authenticated 
            and self.context['request'].user.is_verified
            and (self.context['request'].user.is_supervisor or self.context['request'].user.is_superuser)):
            self.Meta.read_only_fields = ['user', ]

        else:
            self.Meta.read_only_fields = ['user', 'is_approved'] 

    class Meta:
        model = PromotionRequest
        fields = ['id', 'user', 'is_approved']
    
    def to_representation(self, instance):
        request = self.context.get('request')
        rep = super().to_representation(instance)
        rep['user'] = ProfileSerializer(instance.user, context={'request':request}).data
        return rep

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user.profile

        if PromotionRequest.objects.filter(user=user, is_approved=True).exists():
            raise serializers.ValidationError("You cannot submit a new application because your previous application has been approved.")
        
        if user.user.is_staff:
            raise serializers.ValidationError('Your account has now been upgraded.')
        
        validated_data['user'] = user
        promotionRequest = PromotionRequest.objects.create(**validated_data)
        return promotionRequest
    
    def update(self, instance, validated_data):
        request = self.context.get('request')
        print('instance.is_approved ->', instance.is_approved)

        if validated_data['is_approved'] and request.user.is_supervisor:
            if request.user.is_supervisor or request.user.is_superuser:
                instance.user.user.is_staff = True
                instance.user.user.save()

        response = super().update(instance, validated_data)
        return response


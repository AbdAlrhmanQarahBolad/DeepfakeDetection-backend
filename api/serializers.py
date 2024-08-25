from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.validators import UniqueValidator
from .voice_utils.voice_validation import validate_is_audio_and_size
from .models import get_user_via_identifier,Call,CallStatus,UserVoice
from django.db.models import Q


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'password','last_name']
        extra_kwargs = {'password': {'write_only': True}}
    


class CreateUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all())])
    username = serializers.CharField(validators=[UniqueValidator(queryset=User.objects.all())])
    audio_file = serializers.FileField(max_length=None, allow_empty_file=False)

    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'id','audio_file']
        extra_kwargs = {
            'password': {'required': True},
            'email': {'required': True, 'unique': True},
            'username': {'required': True, 'unique': True},
            'last_name': {'required': True},
            'first_name': {'required': True},
            
        }

    def validate(self, attrs):
        email = attrs.get("email", "").strip().lower()
        if User.objects.filter(email=email).exists():
            pass  # You've commented out the validation error for email uniqueness
        return attrs
    
    def validate_audio_file(self, value):
        validate_is_audio_and_size(value)
        return value
    

class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'password', 'last_name']
        extra_kwargs = {
            'password': {'write_only': True},  
        }

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password is not None:
            user.set_password(password)
        user.save()
        return user
     
   
class LoginUserSerializer(serializers.Serializer):
    password = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False)
    identifier = serializers.CharField()
    
    def validate(self, attrs):
        identifier = attrs.get('identifier')
        password = attrs.get('password')

        if not identifier:
            raise serializers.ValidationError("Please provide an identifier (either email or username).")
        if not password:
            raise serializers.ValidationError("Password is required!")

        # Attempt to fetch the user by email or username
        try:
            user = User.objects.get(email=identifier.lower()) if User.objects.filter(email=identifier).exists() else User.objects.get(username=identifier)
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist!")

        # Authenticate the user
        authenticated_user = authenticate(request=self.context.get('request'), username=user.username, password=password)

        if not authenticated_user:
            raise serializers.ValidationError("Invalid credentials")

        attrs['user'] = authenticated_user
        return attrs



class LoginUserVoiceSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    audio_file = serializers.FileField(max_length=None, allow_empty_file=False)

    def validate_audio_file(self, value):
        validate_is_audio_and_size(value)
        return value

    def validate(self, attrs):
        identifier = attrs.get('identifier')
        audio_file = attrs.get('audio_file')
        # Ensure exactly one of email or username is provided
        if not identifier:
            raise serializers.ValidationError("Please provide an identifier.")
        elif User.objects.filter(email=identifier.lower().strip()).exists():
            attrs['email'] = identifier.lower().strip()
        elif User.objects.filter(username=identifier).exists():
            attrs['username'] = identifier
        else:
            raise serializers.ValidationError("User does not exist!")
        # Authenticate the user
        if attrs.get('username',None) is not None:
            authenticated_user = authenticate(request=self.context.get('request'), username=attrs.get('username'), audio_file=audio_file)
        else:
            authenticated_user = authenticate(request=self.context.get('request'), email=attrs.get('email'), audio_file=audio_file)
            

        if not authenticated_user:
            raise serializers.ValidationError("Invalid credentials....")

        attrs['user'] = authenticated_user
        return attrs
 
    
    
    

class SaveUserVoiceSerializer(serializers.Serializer):
    audio_file = serializers.FileField(max_length=None, allow_empty_file=False)
    def validate_audio_file(self, value):
        validate_is_audio_and_size(value)
        return value
    

class DeactivateUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    is_active = serializers.IntegerField()
    def validate(self, attrs):
        id = attrs.get('id')
        if not User.objects.filter(id = id).exists():
            raise serializers.ValidationError("User does not exists!")
        is_active = attrs.get('is_active')
        if is_active not in [0,1]:
            raise serializers.ValidationError("is_active must be a boolean value 0 or 1")
        return attrs
    
    
class GetRandomTextSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    def validate(self, attrs):
        identifier:str = attrs.get('identifier')
        if not identifier:
            raise serializers.ValidationError("Please provide an identifier (either email or username).")
        if not User.objects.filter(email=  identifier.lower().strip()).exists()\
            and not User.objects.filter(username = identifier).exists():
                raise serializers.ValidationError("User does not exists!")
            
        return attrs

class CreateCallSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    
    def validate(self, attrs):
        identifier:str = attrs.get('identifier')
    
        if not identifier:
            raise serializers.ValidationError("Please provide an identifier (either email or username).")
    
        
        recipient = get_user_via_identifier(identifier=identifier)
        user = self.context.get('request').user
        if identifier == user.username or identifier.strip().lower() == user.email:
            raise serializers.ValidationError("You cann't call your self")
        
        if Call.objects.filter(
                Q(recipient = recipient),
                status__in=[CallStatus.CREATED.value, CallStatus.RUNNING.value]
            ).exists():
            raise serializers.ValidationError("The recipient has a call right now!")
        return attrs
        
class CallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Call
        fields = ['id', 'caller', 'recipient', 'status']
        read_only_fields = ('caller', 'recipient','id')
        
    def validate(self, data):
        """
        Validate that the currently authenticated user is either the caller or the recipient of the call.
        """
        # Retrieve the authenticated user from the serializer's context
        user = self.context['request'].user

        # Fetch the Call instance using the call_id from the URL parameters
        call = self.instance

        # Compare the authenticated user with the caller and recipient of the call
        if user.pk != call.caller.pk and user.pk != call.recipient.pk:
            raise serializers.ValidationError({
                'non_field_errors': [
                    'The currently authenticated user must be either the caller or the recipient of the call.'
                ]
            })

        return data


class CallCheckSerializer(serializers.Serializer):
    audio_file = serializers.FileField(max_length=None, allow_empty_file=False)
    class Meta:
        model = Call
        fields = ['id', 'caller', 'recipient', 'status', 'caller_status', 'recipient_status','audio_file']
    
    def validate_audio_file(self, value):
        validate_is_audio_and_size(value)
        
    
    
class IsDeepFakeAPISerializer(serializers.Serializer):
    audio_file = serializers.FileField(max_length=None, allow_empty_file=False)
    def validate_audio_file(self,value):
        validate_is_audio_and_size(value)
        return value

class AcceptDeclineIncomingCallsSerializer(serializers.Serializer):
    accept = serializers.BooleanField()

    def validate_accept(self, value):
        # Check if the value is a boolean
        if not isinstance(value, bool):
            raise serializers.ValidationError("Accept field must be a boolean.")
        return value
   
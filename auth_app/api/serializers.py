from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Handles user registration by validating the provided data and creating a new user instance.
    """
    email = serializers.EmailField(required=True, max_length=255)
    fullname = serializers.CharField(required=True, max_length=150)
    password = serializers.CharField(write_only=True, max_length=128)
    repeated_password = serializers.CharField(write_only=True, max_length=128)

    class Meta:
        model = User
        fields = ('fullname', 'email', 'password', 'repeated_password')

    def validate_email(self, value):
        """
        Validates that the email is unique.
        """
        value = value.lower()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already in use.")
        return value

    def validate_fullname(self, value):
        """
        Validates that the fullname (stored as username) is unique.
        """
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This fullname is already in use.")
        return value
    
    def validate(self, data):
        """
        Validates that the repeated password matches the original password.
        """
        password = data.get('password')
        if password != data.get('repeated_password'):
            raise serializers.ValidationError("Passwords must match.")
        return data

    def save(self, **kwargs):
        """
        Creates and returns a new user instance after validating the data.
        """
        validated_data = self.validated_data
        user = User(
            username=validated_data['fullname'],
            email=validated_data['email']
        )
     
        user.set_password(validated_data['password'])
        user.save()
        return user



class LoginSerializer(serializers.ModelSerializer):
    """
    Serializer for user login.
    Validates that the provided email and password are correct.
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'password')

    def validate(self, data):
        """
        Validates the email and password combination.
        """
        email = data.get('email')
        password = data.get('password')

        if email and password:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid email or password.")

            if not user.check_password(password):
                raise serializers.ValidationError("Invalid email or password.")
        else:
            raise serializers.ValidationError("Both email and password are required.")

        data['user'] = user
        return data
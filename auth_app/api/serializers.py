from django.contrib.auth.models import User
from rest_framework import serializers


class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)
    fullname = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['fullname', 'email', 'password', 'repeated_password']
        extra_kwargs = {
            'password': {'write_only': True},
            'fullname': {'required': True},
            'email': {'required': True},
        }

    

    def save(self, **kwargs):
        password = self.validated_data['password']
        repeated_password = self.validated_data['repeated_password']


        if password != repeated_password:
            raise serializers.ValidationError({"password": "Passwords must match."})
       
        if User.objects.filter(email=self.validated_data['email']).exists():
            raise serializers.ValidationError("Email is already in use.")


        user = User(
            username=self.validated_data['fullname'],
            email=self.validated_data['email']
        )
     
        user.set_password(password)
        user.save()
        return user


    def validate_fullname(self, value):
        if " " in value:
            return value
        return value

class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['email', 'password']

    def validate(self, data):
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
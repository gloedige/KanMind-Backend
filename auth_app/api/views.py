from rest_framework.views import APIView
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import RegistrationSerializer, LoginSerializer
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from auth_app.utils import create_user_object

class RegisterView(APIView):
    """
    Handles the registration process by validating the provided data and creating a new user instance.
    """
    permission_classes = [AllowAny]
    def post(self, request):
        """
        Handles POST requests for user registration.
        Validates the provided data and creates a new user instance if valid.
        """
        serializer = RegistrationSerializer(data=request.data)

        try:
            return self.check_and_save(serializer)
        except serializers.ValidationError as e:
            return Response({'error': e.detail}, status=status.HTTP_400_BAD_REQUEST)
               
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def check_and_save(self, serializer):
        """
        Validates the serializer and saves the user instance if valid.
        Returns a response with the created user's data.
        """
        serializer.is_valid(raise_exception=True)
        save_account = serializer.save()
        data = create_user_object(save_account)
        return Response(data, status=status.HTTP_201_CREATED)
        

class CustomLoginView(ObtainAuthToken):
    """
    Handles user login by validating the provided email and password.
    Returns the user's data if the credentials are correct.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handles POST requests for user login.
        Validates the provided email and password and returns the user's data if valid.
        """
        serializer = LoginSerializer(data=request.data)

        data = {}
        if serializer.is_valid():
            user = serializer.validated_data['user']
            data = create_user_object(user)
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = {
                "errors": serializer.errors
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """
    Handles user logout by deleting the user's authentication token.
    Returns a success message upon successful logout.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Handles POST requests for user logout.
        Deletes the user's authentication token and returns a success message.
        """
        request.user.auth_token.delete()  # Token löschen
        return Response({"detail": "Logout successful. Token was deleted."}, status=status.HTTP_200_OK)


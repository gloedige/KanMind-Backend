from rest_framework.views import APIView
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import RegistrationSerializer, LoginSerializer
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # raise Exception("Test 500 error")  # This will raise a 500 error for testing purposes;

        serializer = RegistrationSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            save_account = serializer.save()
            token, created = Token.objects.get_or_create(user=save_account)
            data = {
                'token': token.key,
                'fullname': save_account.username,  # Assuming you want to return the username as fullname
                'email': save_account.email,
                'user_id': save_account.id,
            }
            return Response(data, status=status.HTTP_201_CREATED)
        
        except serializers.ValidationError as e:
            return Response({'error': e.detail}, status=status.HTTP_400_BAD_REQUEST)
               
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class CustomLoginView(ObtainAuthToken):
    permission_classes = [AllowAny]


    def post(self, request):
        serializer = LoginSerializer(data=request.data) # self.serializer_class(data=request.data)


        data = {}
        if serializer.is_valid():
            user = serializer.validated_data['user']


            token, created = Token.objects.get_or_create(user=user)
            data =   {
                    "token": token.key,
                    "fullname": user.username,
                    "email": user.email,
                    "user_id": user.id,
            }


            return Response(data, status=status.HTTP_201_CREATED)
        else:
            data = {
                "errors": serializer.errors
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)


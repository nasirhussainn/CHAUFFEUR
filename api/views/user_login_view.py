from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from ..serializers.user_login_serializer import UserLoginSerializer

User = get_user_model()

class UserLoginView(APIView):
    def post(self, request):
        try:
            serializer = UserLoginSerializer(data=request.data)
            if serializer.is_valid():
                email = serializer.validated_data['email']
                password = serializer.validated_data['password']

                try:
                    user = User.objects.get(email=email)
                except User.DoesNotExist:
                    return Response({"message": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

                if not user.is_active:
                    return Response({"message": "Account is not active. Please verify your email."}, status=status.HTTP_403_FORBIDDEN)

                user = authenticate(request, username=user.username, password=password)
                if user is not None:
                    try:
                        login(request, user)
                    except Exception as e:
                        return Response({"message": f"Login failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                    return Response({"message": "Login successful."}, status=status.HTTP_200_OK)
                else:
                    return Response({"message": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"message": f"Unexpected error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class MostRecentLoginsView(APIView):
    def get(self, request):
        try:
            count = int(request.query_params.get('recent_logins', 5))
            if count < 1:
                count = 5
            elif count > 10:
                count = 10
        except (TypeError, ValueError):
            count = 5

        top_users = User.objects.exclude(last_login=None).order_by('-last_login')[:count]
        data = [
            {
                'id': user.id,
                'email': user.email,
                'last_login': user.last_login,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
            for user in top_users
        ]
        return Response({
            "message": "Most recent logins fetched successfully.",
            "data": {
                "most_recent_logins": data
            }
        }, status=status.HTTP_200_OK)

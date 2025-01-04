from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class TokenViewSet(ViewSet):
    permission_classes = [AllowAny]  # Tidak memerlukan autentikasi untuk mendapatkan token

    def create(self, request):
        """
        POST: Mendapatkan token dengan username dan password
        """
        username = request.data.get('username')  #admin-testing
        password = request.data.get('password')  #testing1234

        if not username or not password:
            return Response({"error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=username, password=password)
        if not user:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }, status=status.HTTP_200_OK)
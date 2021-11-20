from rest_framework_simplejwt import views as simplejwt_views

from cobra.user.api.serializers import (
    JWTTokenObtainPairSerializer,
    JWTTokenRefreshSerializer,
    JWTTokenVerifySerializer,
)


class JWTTokenObtainPairView(simplejwt_views.TokenObtainPairView):
    serializer_class = JWTTokenObtainPairSerializer


class JWTTokenRefreshView(simplejwt_views.TokenRefreshView):
    serializer_class = JWTTokenRefreshSerializer


class JWTTokenVerifyView(simplejwt_views.TokenVerifyView):
    serializer_class = JWTTokenVerifySerializer

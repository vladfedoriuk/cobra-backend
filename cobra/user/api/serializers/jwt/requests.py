from rest_framework_simplejwt import serializers as simplejwt_serializers


class JWTTokenObtainPairSerializer(simplejwt_serializers.TokenObtainPairSerializer):
    pass


class JWTTokenRefreshSerializer(simplejwt_serializers.TokenRefreshSerializer):
    pass


class JWTTokenVerifySerializer(simplejwt_serializers.TokenVerifySerializer):
    pass

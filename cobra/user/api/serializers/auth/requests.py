from djoser.serializers import (
    ActivationSerializer,
    PasswordResetConfirmRetypeSerializer,
    UserCreatePasswordRetypeSerializer,
)
from rest_framework import serializers


class ResendActivationRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordRequestSerializer(ResendActivationRequestSerializer):
    pass


class ResetPasswordConfirmRequestSerializer(PasswordResetConfirmRetypeSerializer):
    pass


class ActivationRequestSerializer(ActivationSerializer):
    pass


class RegisterRequestSerializer(UserCreatePasswordRetypeSerializer):
    pass

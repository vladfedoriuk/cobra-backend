from djoser import serializers as djoser_serializers
from rest_framework import serializers


class ResendActivationRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordRequestSerializer(ResendActivationRequestSerializer):
    pass


class ResetPasswordConfirmRequestSerializer(
    djoser_serializers.PasswordResetConfirmRetypeSerializer
):
    pass


class ActivationRequestSerializer(djoser_serializers.ActivationSerializer):
    pass


class RegisterRequestSerializer(djoser_serializers.UserCreatePasswordRetypeSerializer):
    pass

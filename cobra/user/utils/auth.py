from django.contrib.auth.models import AbstractUser
from django.contrib.auth.tokens import default_token_generator
from djoser import utils as djoser_utils
from rest_framework_simplejwt.tokens import RefreshToken

from cobra.utils.types import JWTPair, UIDTokenPair


def get_jwt_tokens_for_user(user: AbstractUser) -> JWTPair:
    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def get_uid_and_token_for_user(user: AbstractUser) -> UIDTokenPair:
    return {
        "uid": djoser_utils.encode_uid(user.pk),
        "token": default_token_generator.make_token(user),
    }

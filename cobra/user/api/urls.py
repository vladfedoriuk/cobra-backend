from django.urls import path

from .views import (
    AuthUserViewSet,
    JWTTokenObtainPairView,
    JWTTokenRefreshView,
    JWTTokenVerifyView,
)

app_name = "user"

urlpatterns = [
    path(
        "auth/register/",
        AuthUserViewSet.as_view({"post": "create"}),
        name="api-auth-register",
    ),
    path(
        "auth/activate/",
        AuthUserViewSet.as_view({"post": "activation"}),
        name="api-auth-activate",
    ),
    path(
        "auth/activate/resend/",
        AuthUserViewSet.as_view({"post": "resend_activation"}),
        name="api-auth-activate-resend",
    ),
    path(
        "auth/reset_password/",
        AuthUserViewSet.as_view({"post": "reset_password"}),
        name="api-auth-reset-password",
    ),
    path(
        "auth/reset_password/confirm/",
        AuthUserViewSet.as_view({"post": "reset_password_confirm"}),
        name="api-auth-reset-password-confirm",
    ),
    path(
        "auth/jwt/create/",
        JWTTokenObtainPairView.as_view(),
        name="api-auth-jwt-create",
    ),
    path(
        "auth/jwt/refresh/",
        JWTTokenRefreshView.as_view(),
        name="api-auth-jwt-refresh",
    ),
    path(
        "auth/jwt/verify/",
        JWTTokenVerifyView.as_view(),
        name="api-auth-jwt-verify",
    ),
]

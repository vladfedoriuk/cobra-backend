from django.urls import path

from .views import AuthUserViewSet

app_name = "user"

urlpatterns = [
    path(
        "auth/register/",
        AuthUserViewSet.as_view({"post": "create"}),
        name="api-auth-register",
    )
]

from djoser import views as djoser_views
from djoser.conf import settings as djoser_settings
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from cobra.user.tasks import send_activation_email


class AuthUserViewSet(djoser_views.UserViewSet):
    def perform_create(self, serializer):
        user = serializer.save()
        if djoser_settings.SEND_ACTIVATION_EMAIL:
            send_activation_email.apply_async(kwargs={"user_pk": user.pk})

    @action(detail=False, methods=["post"])
    def activation(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        user.is_active = True
        user.save(update_fields=["is_active"])
        return Response(status=status.HTTP_204_NO_CONTENT)

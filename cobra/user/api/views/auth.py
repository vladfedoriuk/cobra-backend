from djoser import views as djoser_views
from djoser.conf import settings as djoser_settings
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from cobra.user.tasks import send_activation_email


class AuthUserViewSet(djoser_views.UserViewSet):
    def perform_create(self, serializer):
        """
        Copies the original Djoser implementation whereas adding custom
        activation email delivery, and getting rid of
        the confirmation email and signals.

        :param serializer: Serializer
        :return: Response
        """
        user = serializer.save()
        if djoser_settings.SEND_ACTIVATION_EMAIL:
            send_activation_email.apply_async(kwargs={"user_pk": user.pk})

    @action(detail=False, methods=["post"])
    def activation(self, request, *args, **kwargs):
        """
        Copies the original Djoser implementation whereas getting rid of
        the confirmation email and signals.

        :param request: HttpRequest
        :param args:
        :param kwargs:
        :return: Response
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        user.is_active = True
        user.save(update_fields=["is_active"])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["post"])
    def resend_activation(self, request, *args, **kwargs):
        """
        Copies the original Djoser implementation whereas replacing email
        delivery logic with a custom one.

        :param request: HttpRequest
        :param args:
        :param kwargs:
        :return: Response
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.get_user(is_active=False)

        if not djoser_settings.SEND_ACTIVATION_EMAIL or not user:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        send_activation_email.apply_async(kwargs={"user_pk": user.pk})

        return Response(status=status.HTTP_204_NO_CONTENT)

from djoser import views as djoser_views
from djoser.compat import get_user_email
from djoser.conf import settings as djoser_settings


class AuthUserViewSet(djoser_views.UserViewSet):
    def perform_create(self, serializer):
        user = serializer.save()
        if djoser_settings.SEND_ACTIVATION_EMAIL:
            context = {"user": user}
            to = [get_user_email(user)]
            # TODO: add activation mail sending.
            pass

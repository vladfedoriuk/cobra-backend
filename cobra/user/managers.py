from typing import Optional, Tuple, cast

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    use_in_migrations: bool = True

    def __parse_params(
        self,
        username: str,
        email: str,
        first_name: str,
        last_name: str,
        password: Optional[str] = None,
    ) -> Tuple[str, str, str, str, str]:
        if not username:
            raise ValueError("Users must have the username")

        if not email:
            raise ValueError(_("Users must have an email address"))

        if not first_name:
            raise ValueError(_("Users must have the first name"))

        if not last_name:
            raise ValueError(_("Users must have the last name"))

        if not password:
            password = self.make_random_password()

        return (
            username,
            email,
            first_name,
            last_name,
            password,
        )

    def _create_user(
        self,
        username: str,
        email: str,
        first_name: str,
        last_name: str,
        password: Optional[str] = None,
        **kwargs
    ) -> AbstractUser:
        """
        Creates and saves a User with the given username, email, fist_name, last_name and password.
        """
        username, email, first_name, last_name, password = self.__parse_params(
            username, email, first_name, last_name, password
        )
        user: AbstractUser = cast(
            AbstractUser,
            self.model(
                username=username,
                email=self.normalize_email(email),
                first_name=first_name,
                last_name=last_name,
                **kwargs,
            ),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(
        self,
        username: str,
        email: str,
        first_name: str,
        last_name: str,
        password: Optional[str] = None,
        **kwargs
    ) -> AbstractUser:
        kwargs.setdefault("is_staff", False)
        kwargs.setdefault("is_superuser", False)
        return self._create_user(
            username, email, first_name, last_name, password, **kwargs
        )

    def create_superuser(
        self,
        username: str,
        email: str,
        first_name: str,
        last_name: str,
        password: Optional[str] = None,
        **kwargs
    ) -> AbstractUser:
        """
        Creates and saves a superuser with the given username, email, first_name, last_name and password.
        """
        kwargs.setdefault("is_staff", True)
        kwargs.setdefault("is_superuser", True)

        if kwargs.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if kwargs.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self._create_user(
            username, email, first_name, last_name, password, **kwargs
        )

from typing import Optional, Union

from cobra.utils.test import fake

USER_CREATE_DATA: dict[str, Optional[Union[str, bool]]] = {
    "username": "test_user",
    "first_name": fake.first_name(),
    "last_name": fake.last_name(),
    "email": fake.email(),
    "password": "pass4test321!",
}

USER_REGISTER_DATA: dict[str, Optional[Union[str, bool]]] = USER_CREATE_DATA | {
    "re_password": USER_CREATE_DATA["password"],
}

from typing import Literal, Optional

HTTP_METHODS = Optional[
    list[
        Literal[
            "GET",
            "POST",
            "DELETE",
            "PUT",
            "PATCH",
            "TRACE",
            "OPTIONS",
            "get",
            "post",
            "delete",
            "put",
            "patch",
            "trace",
            "options",
        ]
    ]
]

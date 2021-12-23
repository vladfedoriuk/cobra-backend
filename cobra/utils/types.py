from typing import TypedDict


class JWTPair(TypedDict):
    refresh: str
    access: str


class UIDTokenPair(TypedDict):
    uid: str
    token: str

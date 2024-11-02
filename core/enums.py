import requests, requests.cookies
import typing

from enum import IntEnum
from dataclasses import dataclass

if typing.TYPE_CHECKING:
    from .http import ClientWrapper

class RentryType(IntEnum):
    CREATE_NEW = 0
    EDIT_EXISTING = 1
    DELETE = 2

class PacketType(IntEnum):
    CONSOLE_INFO = 0x12
    CONSOLE_WARNING = 0x32
    CONSOLE_ERROR = 0x22

    UNKNOWN = 0x99

class BackendPacket(IntEnum):
    BACK_END = 0x01
    HANDLE_COMMAND = 0x02

    GET_CLIENT_ONLINE = 0x11
    GET_CLIENT_INFO = 0x12

    RUN_SERVER_COMMAND = 0x30
    SEND_CLIENT_PACKET = 0x40

    CLIENT_RESPONSE = 0x50

@dataclass
class NetterClient:
    socket_: "ClientWrapper"

    UUID: str
    username: str
    publicAddress: str
    privateAddress: str

@dataclass
class RentryResponse:
    cookies: requests.cookies.RequestsCookieJar
    requests_response: requests.Response
    payload: dict

    edit_code: str
    text: str
    url: str


@dataclass
class RentryContent:
    title: str
    content: str
    publish_date: str
    last_edit: str
    views: int

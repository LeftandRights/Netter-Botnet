import socket
from enum import IntEnum
from typing import TypeVar, Optional

VALUE = TypeVar('U')

class BackendPacket(IntEnum):
    BACK_END = 0x01
    HANDLE_COMMAND = 0x02

    GET_CLIENT_ONLINE = 0x11
    GET_CLIENT_INFO = 0x12

    RUN_SERVER_COMMAND = 0x30
    CLIENT_RESPONSE = 0x50

def create_socketObject() -> socket.socket:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', 2211))
    return s

def send_packet(packetType: BackendPacket, data: str | bytes) -> bytes:
    if isinstance(data, str):
        data = data.encode('utf-8')

    socketObject: socket.socket = create_socketObject()

    packetLength = len(data).to_bytes(4, 'big')
    packetType = packetType.to_bytes(2, 'little')

    socketObject.send(packetLength)
    socketObject.send(packetType)
    socketObject.send(data)

    response: bytes = socketObject.recv(2048)
    socketObject.close()

    return response

def variable(name, default_value: type = list, value: Optional[VALUE] = None) -> VALUE:
    print(globals().get(name))

    if (name not in globals().keys()):
        globals()[name] = default_value() if not value else value
        return globals()[name]

    if (value is not None):
        globals()[name] = value
        return value

    return globals()[name]

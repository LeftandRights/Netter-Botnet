import socket, json
from enum import IntEnum

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

def send_packet(socketObject: socket.socket, packetType: BackendPacket, data: str | bytes) -> None:
    if isinstance(data, str):
        data = data.encode('utf-8')

    packetLength = len(data).to_bytes(4, 'big')
    packetType = packetType.to_bytes(2, 'little')

    socketObject.send(packetLength)
    socketObject.send(packetType)
    socketObject.send(data)

    if (response := socketObject.recv(1024)):
        print(json.loads(response))

def main() -> None:
    socketObject: socket.socket = create_socketObject()
    send_packet(socketObject, BackendPacket.GET_CLIENT_ONLINE, '0')

if __name__ == '__main__':
    main()

import socket, pickle, time
from loguru import logger

from ..http import ClientWrapper
from ..enums import PacketType


class Connect(socket.socket, ClientWrapper):
    def __init__(self, serverAddress: str, deviceInformation: dict) -> None:
        socket.socket.__init__(self, socket.AF_INET, socket.SOCK_STREAM)
        ClientWrapper.__init__(self, self)

        self.serverHost, self.serverPort = serverAddress.split(":")
        self.deviceInformation: dict = deviceInformation
        self.connected: bool = True

    def disconnect(self) -> None:
        logger.error("Connection reset by server, reconnecting..")
        self.connected = False

    def connect_(self) -> None:
        try:
            self.connect((self.serverHost, int(self.serverPort)))

            logger.info("Conntected to server -> %s:%s" % (self.serverHost, self.serverPort))
            self.send_(packetType = PacketType.RAW_PACKET, data=pickle.dumps(self.deviceInformation))

            while self.connected:
                try:
                    data_buffer: bytes = self.receive()

                    if not data_buffer:
                        break

                    print(data_buffer)

                except ConnectionResetError:
                    break

            self.disconnect()

        except (ConnectionResetError, OSError):
            self.disconnect()

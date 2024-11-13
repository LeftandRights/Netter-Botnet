import socket, pickle
from loguru import logger

from ..http import ClientWrapper
from ..enums import PacketType
from .handler import serverHandler

class Connect(socket.socket, ClientWrapper, serverHandler):
    def __init__(self, serverAddress: str, deviceInformation: dict) -> None:
        socket.socket.__init__(self, socket.AF_INET, socket.SOCK_STREAM)
        ClientWrapper.__init__(self, self)
        serverHandler.__init__(self, self)

        self.serverHost, self.serverPort = serverAddress.split(":")
        self.deviceInformation: dict = deviceInformation
        self.connected: bool = True
        self._socketInstance.send

    def disconnect(self) -> None:
        logger.error("Connection reset by server, reconnecting..")
        self.connected = False

    def connect_(self) -> None:
        try:
            self.connect((self.serverHost, int(self.serverPort)))

            logger.info("Conntected to server -> %s:%s" % (self.serverHost, self.serverPort))
            self.send_(packetType = PacketType.UNKNOWN, data = pickle.dumps(self.deviceInformation))

            while self.connected:
                try:
                    if not (data_buffer := self.receive()):
                        break

                    logger.info(f'New incoming packet[{data_buffer.packetType}]: {data_buffer.data.decode()}')
                    self.handle(data_buffer.data)

                except ConnectionResetError:
                    break

            self.disconnect()

        except (ConnectionResetError, OSError):
            self.disconnect()

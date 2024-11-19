import threading, typing

from .enums import PacketType

if typing.TYPE_CHECKING:
    from .http import ClientWrapper, NetterServer
    from .enums import NetterClient


class ClientHandler(threading.Thread):
    def __init__(self, socketClient: "ClientWrapper", netClient: "NetterClient", netServer: "NetterServer") -> None:
        threading.Thread.__init__(self)

        self.socketClient: "ClientWrapper" = socketClient
        self.netServer: "NetterServer" = netServer
        self.netClient: "NetterClient" = netClient

        self.isConnected: bool = True

    def disconnect(self) -> None:
        self.netServer.console_log(
            "%s (%s) just left the server"
            % (self.netClient.publicAddress, self.netClient.username)
        )

        self.isConnected = False
        self.socketClient.socket.close()
        self.netServer.remove(self.netClient)

    def run(self) -> None:
        self.netServer.console_log(
            "%s (%s) just hopped onto the server!"
            % (self.netClient.publicAddress, self.netClient.username)
        )

        while self.isConnected:
            if (not (response := self.socketClient.receive())):
                # If the `receive()` function retruns an integer, it means the packet that
                # are being sent is involving with console stdout, no need to handle.

                if not response:
                    self.disconnect()

            if (isinstance(response, int)):
                continue

            if (response.packetType == PacketType.COMMAND_RESPONSE and self.netClient.socket_.responseFunction):
                self.netClient.socket_.responseFunction(self.netServer, self.netClient, response)
                self.netClient.socket_.responseFunction = None

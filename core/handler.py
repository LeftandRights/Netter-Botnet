import threading, typing

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
        self.netServer.connectionList.remove(self.netClient)

    def run(self) -> None:
        self.netServer.console_log(
            "%s (%s) just hopped onto the server!"
            % (self.netClient.publicAddress, self.netClient.username)
        )

        while self.isConnected:
            if (not (data := self.socketClient.receive())) or isinstance(data, int):
                # If the `receive()` function retruns an integer, it means the packet that
                # are being sent is involving with console stdout, no need to handle.

                if not data:
                    self.disconnect()

            self.netServer.console_log(len(str(data.decode())))

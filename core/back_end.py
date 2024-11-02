import socket, threading, json, typing
from dataclasses import fields

from .enums import BackendPacket
from .input import InputHandler

if (typing.TYPE_CHECKING):
    from .http import NetterServer

class backEnd_server(threading.Thread):
    def __init__(self, netServer: "NetterServer") -> None:
        threading.Thread.__init__(self)

        self.inputHandler: InputHandler = InputHandler(netServer)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = json.load(open('config.json', 'r')) \
            .get('serverSideAddress', '127.0.0.1:2211')

        self.netServer: "NetterServer" = netServer
        self._socket.bind(((_ := self.address.split(':'))[0], int(_[1])))

    def _handle(self, _client: socket.socket) -> None:
        packetLength: int = int.from_bytes(_client.recv(4), "big")
        packet_type: int = int.from_bytes(_client.recv(2), "little")

        data: bytes = _client.recv(packetLength).decode('UTF-8')

        if (packet_type == BackendPacket.GET_CLIENT_ONLINE):
            if (not self.netServer.connectionList):
                _client.send(b'[]'); return

            clientCollection = []

            for client in self.netServer.connectionList:
                clientData = {}

                for _object in fields(client):
                    if (_object.name == "socket_"): continue
                    clientData[_object.name] = getattr(client, _object.name)

                clientCollection.append(clientData)

            _client.sendall(json.dumps(clientCollection).encode('UTF-8'))

        elif (packet_type == BackendPacket.GET_CLIENT_INFO):
            if (data not in [client.UUID for client in self.netServer.connectionList]):
                _client.send(b'[]')
                return

            client = self.netServer.connectionList[[
                    index for index in range(len(self.netServer.connectionList))
                    if (self.netServer.connectionList[index].UUID == data)
                ][0]
            ]

            clientData = {}

            for _object in fields(client):
                if (_object.name == "socket_"): continue
                clientData[_object.name] = getattr(client, _object.name)

            _client.sendall(json.dumps(clientData).encode('UTF-8'))

        elif (packet_type == BackendPacket.RUN_SERVER_COMMAND):
            currentLogsLength = len(self.netServer.logs)
            self.inputHandler.handle(data)
            newLogsLength = len(self.netServer.logs)

            if (newLogsLength > currentLogsLength):
                _client.send(json.dumps([_[2] for _ in self.netServer.logs[(currentLogsLength):]]).encode('UTF-8'))
                return

            _client.send(b'[]')

        _client.close()

    def run(self) -> None:
        self._socket.listen(10); self.netServer.console_log(
        'Backend server is running on %s' % self.address
        )

        while True:
            client, _ = self._socket.accept()
            threading.Thread(target = self._handle, args = (client,)).start()

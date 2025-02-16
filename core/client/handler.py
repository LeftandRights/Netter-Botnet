import socket, typing, threading

from ..enums import PacketType
from ..commands import loadCommand

if typing.TYPE_CHECKING:
    from .connect import Connect


class serverHandler:
    def __init__(self, socketInstance: socket.socket) -> None:
        self._socketInstance: Connect = socketInstance

    def handle(self, response: str | bytes) -> None:
        if isinstance(response, bytes):
            response = response.decode("utf-8")

        for commandFunction in loadCommand():
            if response.split(" ")[0] not in commandFunction.__aliases__:
                continue

            if commandFunction._generatorFunction:
                print("ITS INDEED A GENERATOR FUNCTION")

                def runGenerator() -> None:
                    for data in commandFunction().on_client_receive(self._socketInstance):
                        print("Sending data to server with length: " + str(len(data)))

                        if callable(data):
                            data()
                            continue

                        elif type(data) in (str, bytes):
                            self._socketInstance.send_(packetType=PacketType.COMMAND_RESPONSE, data=data)
                            continue

                threading.Thread(target=runGenerator).start()
                break

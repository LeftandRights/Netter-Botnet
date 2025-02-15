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
            if (splittedResponse := response.split(" "))[0] not in commandFunction.__aliases__:
                continue
            if commandFunction._generatorFunction:

                def runGenerator() -> None:
                    for data in commandFunction().on_client_receive(self._socketInstance):
                        self._socketInstance.send_(packetType=PacketType.COMMAND_RESPONSE, data=data)

                threading.Thread(target=runGenerator).start()
                break

            self._socketInstance.send_(packetType=PacketType.COMMAND_RESPONSE, data=commandFunction().on_client_receive(self._socketInstance))

        # for fn, func in moduleList.items():
        #     if (_splitted_resp := response.split(" "))[0] not in json.loads(fn):
        #         continue

        #     try:
        #         returnValue = func(self._socketInstance, *_splitted_resp[1:])

        #     except TypeError:
        #         returnValue = func(self._socketInstance)

        # if returnValue:
        #     with contextlib.suppress(Exception):
        #         returnValue = bytes(returnValue, "UTF-8")

        #     self._socketInstance.send_(packetType=PacketType.COMMAND_RESPONSE, data=returnValue)

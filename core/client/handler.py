import socket, typing, threading

from ..enums import PacketType
from ..commands import loadCommand, CommandBase
from typing import Type

if typing.TYPE_CHECKING:
    from .connect import Connect


class serverHandler:
    def __init__(self, socketInstance: socket.socket) -> None:
        self._socketInstance: Connect = socketInstance

    def handle(self, response: str | bytes) -> None:
        if isinstance(response, bytes):
            response = response.decode("utf-8")

        for commandFunction in loadCommand():
            if (splitted_response := response.split(" "))[0] not in commandFunction.__aliases__:
                continue

            required_args = commandFunction._required_args(commandFunction.on_client_receive)
            args = splitted_response[1:required_args] if required_args > 1 else []

            if commandFunction._generatorFunction:
                threading.Thread(target=self.execute_generator, args=(commandFunction, args)).start()
                break

            commandFunction().execute(self._socketInstance, *args)
            break

    def execute_generator(self, commandFunction: Type[CommandBase], args: list) -> None:

        for data in commandFunction.on_client_receive(self._socketInstance, *args):
            if callable(data):
                data()

            elif type(data) in (str, bytes):
                self._socketInstance.send_(packetType=PacketType.COMMAND_RESPONSE, data=data)

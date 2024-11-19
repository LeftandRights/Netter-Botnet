import socket, os, importlib
import json, typing, contextlib

from ..enums import PacketType

if typing.TYPE_CHECKING:
    from .connect import Connect

class serverHandler:
    def __init__(self, socketInstance: socket.socket) -> None:
        self._socketInstance: Connect = socketInstance

    def handle(self, response: str | bytes) -> None:
        if isinstance(response, bytes):
            response = response.decode("utf-8")

        fileList = [fileName for fileName in os.listdir("core/command") if fileName.endswith(".py")]
        moduleList = {
            json.dumps(getattr((mod := importlib.import_module("core.command." + fileName[:-3])), "__aliases__", [])):
                getattr(mod, "on_client_receive", lambda: ...)

            for fileName in fileList
        }

        for fn, func in moduleList.items():
            if ((_splitted_resp := response.split(' '))[0] not in json.loads(fn)):
                continue

            try:
                returnValue = func(self._socketInstance, *_splitted_resp[1:])

            except TypeError:
                returnValue = func(self._socketInstance)

        if (returnValue):
            with contextlib.suppress(Exception):
                returnValue = bytes(returnValue, 'UTF-8')

            self._socketInstance.send_(
                packetType = PacketType.COMMAND_RESPONSE,
                data = returnValue
            )

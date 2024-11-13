import socket, os, importlib
import json

class serverHandler:
    def __init__(self, socketInstance: socket.socket) -> None:
        self._socketInstance: socket.socket = socketInstance

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
            if (response.split(' ')[0] not in json.loads(fn)):
                continue

            func(self._socketInstance)

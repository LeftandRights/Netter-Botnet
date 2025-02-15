from typing import TYPE_CHECKING
from dataclasses import fields

from ..commands import CommandBase

if TYPE_CHECKING:
    from ..http import NetterServer


class infoCommand(CommandBase):
    __aliases__ = ["info"]
    __description__ = "Get all information about the client"
    __extra__ = ""

    def execute(self, netServer: "NetterServer", *args) -> None:
        if not args and not netServer.selectedClient:
            # netServer.console_log('No client selected', level = 'ERROR')
            netServer.inputHandler.handle("help info")
            return

        selectedClient = netServer.selectedClient if netServer.selectedClient else netServer.get(UUID=args[0])

        if selectedClient is None:
            netServer.console_log("Provided client does not exist.", level="ERROR")
            return

        objectList = {object.name: getattr(selectedClient, object.name) for object in fields(selectedClient) if (object.name != "socket_")}

        netServer.console_log(f"Info for {selectedClient.username}:")

        for obj, val in objectList.items():
            spaceCount = max(list(map(len, list(objectList.keys())))) + 5
            netServer.console_log("     ↳ %s%s-     %s" % (obj, " " * (spaceCount - len(obj)), repr(val)), level="PLAIN")

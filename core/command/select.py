from typing import TYPE_CHECKING

from ..commands import CommandBase

if TYPE_CHECKING:
    from ..http import NetterServer


class selectCommand(CommandBase):
    __aliases__ = ["select"]
    __description__ = "Select a client for further operations"

    def execute(self, netServer: "NetterServer", *args) -> None:
        if not args:
            netServer.inputHandler.handle("help select")
            return

        if (client := netServer.get(UUID=args[0])) is None:
            netServer.console_log("Provided client does not exist.", level="ERROR")
            return

        netServer.selectedClient = client
        netServer.console_log(netServer.selectedClient.username + " is selected")

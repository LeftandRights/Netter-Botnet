from typing import TYPE_CHECKING
from ..commands import CommandBase, loadCommand

if TYPE_CHECKING:
    from ..http import NetterServer


class helpCommand(CommandBase):
    __aliases__ = ["help", "hlep"]
    __description__ = "Information about the server or the command"

    def execute(self, netServer: "NetterServer", *args) -> None:
        moduleList = {
            commandObject.__aliases__[0]: {
                "aliases": commandObject.__aliases__,
                "description": commandObject.__description__,
                "extras": commandObject.__extra__,
            }
            for commandObject in loadCommand()
        }

        if not args:
            netServer.console_log("For more information on a specific command, type HELP `command-name`")
            spaceCount: str = max([len(module) for module in moduleList.keys()]) + 5

            for moduleName, value in moduleList.items():
                netServer.console_log(
                    "    ↳  %s%s-     %s" % (moduleName.upper(), " " * (spaceCount - len(moduleName)), value["description"]), level="PLAIN"
                )

            return

        commmandName: str = args[0].lower()

        if commmandName not in [alias for value in moduleList.values() for alias in value["aliases"]]:
            netServer.console_log("Command not found: %s" % commmandName, level="ERROR")
            return

        _command = [key for key, value in moduleList.items() if commmandName in value["aliases"]][0]

        netServer.console_log("Commands information: %s" % commmandName)
        netServer.console_log("    ↳  Aliases                :   {}".format(", ".join(moduleList[_command]["aliases"])), level="PLAIN")
        netServer.console_log("    ↳  Command description    :   {}".format(moduleList[_command]["description"]), level="PLAIN")

        if moduleList[_command].get("extras"):
            netServer.console_log("    ↳  Extras                 :   {}".format(moduleList[_command]["extras"]), level="PLAIN")

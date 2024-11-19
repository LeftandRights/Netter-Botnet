from typing import TYPE_CHECKING
import os, importlib

if TYPE_CHECKING:
    from ..http import NetterServer

__aliases__ = ["help", "hlep"]
__description__ = "Information about the server or the command"

def execute(netServer: "NetterServer", *args) -> None:
    fileList = [fileName for fileName in os.listdir("core/command") if fileName.endswith(".py")]
    moduleList = {
        getattr((module := importlib.import_module("core.command." + fileName[:-3])), "__aliases__")[0].lower(): {
            "aliases": getattr(module, "__aliases__"),
            "description": getattr(module, "__description__", "Not Specified")
        }
            for fileName in fileList
    }

    if not args:
        netServer.console_log("For more information on a specific command, type HELP `command-name`")
        spaceCount: str = max([len(module) for module in moduleList.keys()]) + 5

        for moduleName, value in moduleList.items():
            netServer.console_log("    ↳  %s%s-     %s" % (
                moduleName.upper(),
                " " * (spaceCount - len(moduleName)),
                value['description']

            ), level = "PLAIN")

        return

    commmandName: str = args[0].lower()

    if (commmandName not in [alias for value in moduleList.values() for alias in value['aliases']]):
        netServer.console_log("Command not found: %s" % commmandName, level = 'ERROR')
        return

    _command = [key for key, value in moduleList.items() if commmandName in value['aliases']][0]

    netServer.console_log("Commands information: %s" % commmandName)
    netServer.console_log("    ↳  Aliases                :   {}".format(', '.join(moduleList[_command]['aliases'])), level = "PLAIN")
    netServer.console_log("    ↳  Command description    :   {}".format(moduleList[_command]['description']), level = "PLAIN")

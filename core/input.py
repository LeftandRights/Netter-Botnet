import typing, importlib, os

from .enums import NetterClient

if typing.TYPE_CHECKING:
    from logger import Logging

class InputHandler:
    def __init__(self, _logging: "Logging") -> None:
        self.logging: "Logging" = _logging

        # {
        #     ["command name", "command aliases"] = {
        #         "description": "description",
        #         "executor": "callable function"
        #     }
        # }

        self.commandList: dict[list[str], dict[str, str | callable]] = {}

        for filename in os.listdir("core/command"):
            if not (filename.endswith(".py")):
                continue

            module = importlib.import_module(f"core.command.{filename[:-3]}")
            commandName = getattr(module, "__aliases__", filename[:-3])

            if not isinstance(commandName, list):
                continue

            for name in commandName:
                self.commandList[name.lower()] = {
                    "description": getattr(module, "__description__", "Not specified"),
                    "executor": getattr(module, "execute",
                        lambda *_: self.logging.console_log(
                            f"Command executor function is not found for {
                                '\\'.join(getattr(module, '__file__').split('\\')[-2:])
                            }",

                            level = "ERROR",
                        ),
                    ),

                    "on_server_receive": getattr(module, "on_server_receive", None)
                }

    def handle(self, user_input: str) -> None:
        userCommand: str = user_input.split(" ")[0].lower()

        if (not userCommand):
            return

        if userCommand in self.commandList.keys():

                # returnValue: bool = self.commandList[userCommand]["executor"](self.logging.netServer) if ' ' not in user_input \
                #     else self.commandList[userCommand]["executor"](self.logging.netServer, *user_input.split()[1:])

            try:
                if len(user_input.split()) == 1:
                    raise TypeError

                returnValue: NetterClient =  self.commandList[userCommand]["executor"](
                    self.logging.netServer, *user_input.split()[1:]
                )

            except TypeError:
                returnValue: NetterClient = self.commandList[userCommand]["executor"](self.logging.netServer)

            if isinstance(returnValue, NetterClient) and (on_server_receive := self.commandList[userCommand]['on_server_receive']):
                returnValue.socket_.responseFunction = on_server_receive


        else:
            self.on_command_not_found(userCommand)

    def on_command_not_found(self, command: str) -> None:
        self.logging.console_log('The command "%s" not found' % command, level = "ERROR")

    def on_command_error(self, commandName: str, errorMessages: str) -> None:
        self.logging.console_log('An error occurred while executing the command "%s"' % commandName, level = 'ERROR')
        self.logging.console_log('  L Error messages: ' + errorMessages, level = 'PLAIN')

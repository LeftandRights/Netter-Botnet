import typing, importlib, os

if typing.TYPE_CHECKING:
    from logger import C2Server


class InputHandler:
    def __init__(self, _C2Server: "C2Server") -> None:
        self.C2Server: C2Server = _C2Server

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
                        lambda: self.C2Server.console_log(
                            f"Command executor not found for {filename}",
                            level = "ERROR",
                        ),
                    ),
                }

    def handle(self, user_input: str) -> None:
        userCommand: str = user_input.split(" ")[0].lower()

        if (not userCommand):
            return

        if userCommand in self.commandList.keys():
            try:
                if (' ' not in user_input):
                    self.commandList[userCommand]["executor"](self.C2Server.netServer)

                else:
                    self.commandList[userCommand]["executor"](self.C2Server.netServer, *user_input.split()[1:])

            except Exception as e:
                self.on_command_error(userCommand, str(e))

        else:
            self.on_command_not_found(userCommand)

    def on_command_not_found(self, command: str) -> None:
        self.C2Server.console_log('The command "%s" not found' % command, level = "ERROR")

    def on_command_error(self, commandName: str, errorMessages: str) -> None:
        self.C2Server.console_log('An error occurred while executing the command "%s"' % commandName, level = 'ERROR')
        self.C2Server.console_log('Error messages: ' + errorMessages, level = 'ERROR')

import typing
from .commands import loadCommand

if typing.TYPE_CHECKING:
    from logger import Logging


class InputHandler:
    def __init__(self, _logging: "Logging") -> None:
        self.logging: "Logging" = _logging

    def handle(self, user_input: str) -> None:
        if not (userCommand := user_input.split(" ")[0].lower()):
            return

        for command in loadCommand():
            if userCommand not in getattr(command, "__aliases__", []):
                continue

            returnValue = (calledCommand := command()).execute(self.logging.netServer, *(user_input.split()[1:] or []))
            break

        else:
            self.on_command_not_found(userCommand)
            return

        if calledCommand._clientInteraction and returnValue is not None:
            returnValue.socket_.responseFunction = calledCommand.on_server_receive

    def on_command_not_found(self, command: str) -> None:
        self.logging.console_log('The command "%s" not found' % command, level="ERROR")

    def on_command_error(self, commandName: str, errorMessages: str) -> None:
        self.logging.console_log('An error occurred while executing the command "%s"' % commandName, level="ERROR")
        self.logging.console_log("  L Error messages: " + errorMessages, level="PLAIN")

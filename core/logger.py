import curses
import threading

from datetime import datetime
from typing import Optional, Literal, TYPE_CHECKING
from contextlib import suppress
from os import _exit

from .input import InputHandler
from .enums import PacketType

if TYPE_CHECKING:
    from curses import _CursesWindow
    from .http import NetterServer, NetterClient


class Logging:
    logs: list[tuple[str, str, str]] = list()
    color: dict[str, int] = {1: curses.COLOR_GREEN, 2: curses.COLOR_RED, 3: curses.COLOR_YELLOW, 4: curses.COLOR_CYAN}

    def __init__(self, netServer: "NetterServer") -> None:
        curses.wrapper(self._initialize)
        self.netServer: "NetterServer" = netServer
        self.inputHandler = InputHandler(self)

        self.selectedClient: "NetterClient" = None

        if curses.has_colors():
            curses.start_color()

            for key, value in self.color.items():
                curses.init_pair(key, value, curses.COLOR_BLACK)

        threading.Thread(target=self.userInput_handler).start()

    def _initialize(self, stdsrc: "_CursesWindow") -> None:
        self.stdscr: "_CursesWindow" = stdsrc
        self.height, self.width = self.stdscr.getmaxyx()

        self.logWindow: _CursesWindow = curses.newwin(self.height - 3, self.width, 0, 0)
        self.inputWindow: _CursesWindow = curses.newwin(1, self.width, self.height - 1, 0)

    def input(self, prompt: Optional[str] = " > ") -> str:

        if self.netServer.selectedClient:
            prompt = self.netServer.selectedClient.UUID + " > "

        self.inputWindow.clear()
        self.inputWindow.addstr(0, 0, prompt)
        self.inputWindow.refresh()

        curses.echo()
        user_input = self.inputWindow.getstr(0, len(prompt)).decode("utf-8")

        curses.noecho()
        return user_input

    def console_log(self, message: str, level: Optional[Literal["INFO", "WARNING", "ERROR", "PLAIN"]] = "INFO") -> None:
        self.logs.append((datetime.now().strftime("%Y-%m-%d %H:%M:%S"), level, message))

        # if len(self.logs) > (self.height - 3):
        #     self.logs = self.logs[1:]

        self.display_logs()

    def display_logs(self) -> None:
        curses.curs_set(0)
        self.stdscr.clear()
        self.logWindow.clear()

        for idx, (timestamp, _level, msg) in enumerate(
            self.logs if len(self.logs) < self.height - 3 else self.logs[len(self.logs) - (self.height - 3) :]
        ):
            with suppress(Exception):
                if _level != "PLAIN":
                    self.logWindow.attron(curses.color_pair(1))
                    self.logWindow.addstr(idx, 0, timestamp)
                    self.logWindow.attroff(curses.color_pair(1))

                    if _level == "ERROR":
                        self.logWindow.attron(curses.color_pair(2))

                    elif _level == "WARNING":
                        self.logWindow.attron(curses.color_pair(3))

                    self.logWindow.addstr(idx, len(timestamp) + 1, f"[{_level}] ")
                    self.logWindow.attroff(curses.color_pair(2 if _level == "ERROR" else 3))

                    self.logWindow.attron(curses.color_pair(4))
                    self.logWindow.addstr(idx, len(timestamp) + len(_level) + 4, msg)
                    self.logWindow.attroff(curses.color_pair(4))
                    continue

                self.logWindow.attron(curses.color_pair(4))
                self.logWindow.addstr(idx, 0, msg)
                self.logWindow.attroff(curses.color_pair(4))

        self.logWindow.refresh()

    def userInput_handler(self) -> None:

        while True:
            user_input = self.input()

            if user_input.startswith("msg "):
                for client in self.netServer.connectionList:
                    client.socket_.send_(PacketType.UNKNOWN, user_input.encode("UTF-8"))

            if user_input.lower() == "exit":
                if not self.netServer.selectedClient:
                    self.stdscr.clear()
                    self.stdscr.refresh()
                    curses.endwin()
                    _exit(0)

                self.netServer.selectedClient = None
                self.netServer.console_log("Type `exit` once again to exit.")
                continue

            if user_input.lower() in ["clear", "cls"]:
                self.logs = list()
                self.display_logs()
                self.console_log("All log messages has been cleared")
                continue

            if user_input:
                self.inputHandler.handle(user_input=user_input)

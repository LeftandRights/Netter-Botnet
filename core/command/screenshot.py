from typing import TYPE_CHECKING
import os, importlib

if TYPE_CHECKING:
    from ..http import NetterServer

__aliases__ = ["screenshot", "ss", "sso", "testing"]
__description__ = "Take a screenshot from the client desktop"

def executes(netServer: "NetterServer") -> None:
    ...

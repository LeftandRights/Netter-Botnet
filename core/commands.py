from abc import ABC, abstractmethod
from typing import List, Callable, Type, TYPE_CHECKING
import os, importlib, inspect

if TYPE_CHECKING:
    from .http import NetterServer, NetterClient
    from .enums import ClientResponse
    from .client.connect import Connect


class CommandBase(ABC):
    _clientInteraction: bool = False
    _generatorFunction: bool = False
    _acceptOptionalArguements: bool = False

    __aliases__: List[str] = []
    __description__: str = "No description provided."
    __extra__: str = ""

    _instances = {}

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__new__(cls)
        return cls._instances[cls]

    @abstractmethod
    def execute(self, netServer: "NetterServer") -> None:
        pass

    def on_server_receive(self, netServer: "NetterServer", client: "NetterClient", packet: "ClientResponse") -> None:
        pass

    def on_client_receive(self, serverHandler: "Connect") -> None:
        pass

    def _required_args(self, function: Callable) -> int:
        return len(
            [
                p
                for p in inspect.signature(function).parameters.values()
                if p.default == inspect.Parameter.empty
                and p.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
            ]
        )


def loadCommand() -> tuple[Type[CommandBase]]:
    commands = []

    for fileName in [fileName for fileName in os.listdir("core/command") if fileName.endswith(".py")]:

        module_name = "core.command." + fileName[:-3]
        module = importlib.import_module(module_name)

        for atrName in dir(module):
            attributes = getattr(module, atrName)

            if not (isinstance(attributes, type) and issubclass(attributes, CommandBase) and attributes is not CommandBase):
                continue

            if "on_client_receive" not in attributes.__abstractmethods__:
                attributes._clientInteraction = True

            attributes._generatorFunction = inspect.isgeneratorfunction(attributes.on_client_receive)
            attributes._acceptOptionalArguements = any(
                p.kind == inspect.Parameter.VAR_POSITIONAL for p in inspect.signature(attributes().execute).parameters.values()
            )

            commands.append(attributes())

    return tuple(commands)

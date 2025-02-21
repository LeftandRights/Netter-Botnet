import typing

if typing.TYPE_CHECKING:
    from .enums import PacketType
    from .http import NetterServer, NetterClient


class ConnectionBucket:
    __connection: list["NetterServer"] = list()

    def __init__(self, netServer: "NetterServer") -> None:
        self.netServer: "NetterServer" = netServer

    @property
    def connection_list(self) -> list["NetterServer"]:
        return self.__connection

    def append(self, client: "NetterClient") -> bool:
        if client not in self.__connection:
            self.__connection.append(client)
            return True

        return False

    def get(self, **key) -> typing.Union["NetterClient", None]:
        client = None

        for _key in key:
            for _client in self.__connection:
                if hasattr(_client, _key) and getattr(_client, _key) == key[_key]:
                    client = _client
                    break

        return client

    def remove(self, client: typing.Optional["NetterClient"] = None, **key) -> bool: ...

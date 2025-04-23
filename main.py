# ----------------------------------------------------------------------------
#                            => CREDITS <=
# ----------------------------------------------------------------------------
#                 HACK: Developed and maintained by VXNET
#            ✦ Do not copy code. Protect your files securely. ✦
#                     Best Hackers in the Business!
#                      Web: http://lefeu.nvnet.pl
# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
__program__ = "discord_auto_responder"
__version__ = "0.0.1"
# ----------------------------------------------------------------------------

from colorama import Fore, init as clinit

clinit(autoreset=True)

import json, sys

from vendor.setup import Setup
# from vendor.protector import Protector

# Protector().run()
Setup().run()

def parseConfig(config_file = "./DARconfig/config.json"):
    data = None
    with open(config_file, "r+") as f:
        data = f.read()
    try:
        config = json.loads(data)
        return config
    except:
        print(f"{Fore.CYAN}[ {Fore.RED}JSON CONFIG INVALID {Fore.CYAN}] {Fore.LIGHTWHITE_EX}Configuration file have errors, please check config.json syntax and relaunch program")
        input(f"{Fore.LIGHTBLACK_EX}PRESS ANY KEY TO CONTINUE{Fore.RESET}")
        sys.exit(90284)

# from vendor.vxauth import VXNET_AUTHENTICATION_SYSTEM, getLatestProgramVersion

# auth_api = VXNET_AUTHENTICATION_SYSTEM()
config = parseConfig()

# Protector().run()

# json_auth_data = auth_api.authenticate(
#     __program__,
#     "./DARconfig/config.json",
#     "license"
# )

json_auth_data = {
    "expiration_date": "LIFETIME",
    "hwid": "FFFF-FFFF-FFFF-FFFF"
}

# Protector().run()

# __latest__ = getLatestProgramVersion(__program__)

__latest__ = "0.0.1"

# Protector().run()

# Load everything
from modules.ui import GraphicalInterface

if __name__ == "__main__":
    try:
        GraphicalInterface(json_auth_data, __version__, __latest__)
    except KeyboardInterrupt:
        sys.exit()
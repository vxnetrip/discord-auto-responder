# ----------------------------------------------------------------------------
#                            => CREDITS <=
# ----------------------------------------------------------------------------
#                 HACK: Developed and maintained by VXNET
#                        ✦ Do not copy code. ✦
#               ✦ Discord: https://discord.gg/HmGHGww2kY ✦
#                      Web: http://lefeu.nvnet.pl
# ----------------------------------------------------------------------------

import sys, os
import json
from colorama import Fore, init as clinit

clinit(autoreset=True)

def read_config(config_file = "./DARconfig/config.json") -> dict:
    data = None
    with open(config_file, "r+") as f:
        data = f.read()
    try:
        config = json.loads(data)
        return config
    except:
        print(f"{Fore.CYAN}[ {Fore.RED}JSON CONFIG INVALID {Fore.CYAN}] {Fore.LIGHTWHITE_EX}Please check {os.getcwd()}DARconfig/config.json syntax and relaunch program.")
        input(f"{Fore.LIGHTBLACK_EX}PRESS ANY KEY TO CONTINUE{Fore.RESET}")
        sys.exit(90284)

def write_config(data: str | dict, config_file = "./DARconfig/config.json"):
    if isinstance(data, dict):
        data = json.dumps(data, indent=4)


    if os.path.exists(config_file):
        with open(config_file, "w+") as cf:
            cf.write(data)
    else:
        print(f"{Fore.CYAN}[ {Fore.RED}JSON CONFIG MISSING {Fore.CYAN}] {Fore.LIGHTWHITE_EX}90281")
        input(f"{Fore.LIGHTBLACK_EX}PRESS ANY KEY TO CONTINUE{Fore.RESET}")
        sys.exit(90283)
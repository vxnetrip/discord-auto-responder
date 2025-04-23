# ----------------------------------------------------------------------------
#                            => CREDITS <=
# ----------------------------------------------------------------------------
#                 HACK: Developed and maintained by VXNET
#                        ✦ Do not copy code. ✦
#               ✦ Discord: https://discord.gg/HmGHGww2kY ✦
#                      Web: http://lefeu.nvnet.pl
# ----------------------------------------------------------------------------

import time
import os
from colorama import Fore, init as clinit
from rich.table import Table
from rich.console import Console
from threading import Thread
import requests

from .utils import read_config
from .server import run_flask_server

clinit()

from .utils import read_config
from .current_state import State_Flask, State_AutoResponder

def process_autostart():
    if read_config()['DISCORD_AUTO_RESPONDER']['autostart']:
        response = requests.get(f"http://127.0.0.1:{read_config()['SERVER']['port']}/start-auto-responder-thread")


def refresh_web_status():
    while True:
        if State_Flask.status == "OFF":
            thread_flask_server = Thread(target=run_flask_server, daemon=True)
            thread_flask_server.start()
            State_Flask.status = "PENDING"
        else:

            try:
                response = requests.get( f"http://127.0.0.1:{read_config()['SERVER']['port']}" )
                if response.status_code == 200:
                    State_Flask.status = "OPERATING NORMALLY"
                    t = Thread(target=process_autostart, daemon=True)
                    t.start()
                else:
                    State_Flask.status = "ERROR"
            except:
                State_Flask.status = "ERROR"
        
        time.sleep(3)


class GraphicalInterface:
    def __init__(self, json_auth_data: dict, current_version: str, latest_version: str):
        self.expiration_date = json_auth_data.get('expiration_date')
        self.hwid = json_auth_data.get('hwid')
        self.current_version = current_version
        self.latest_version = latest_version
        self.main() # Call MAIN entry

    # NOTE: Clear console
    def _clear_console(self):
        os.system('cls' if os.name == "nt" else "clear")

    # NOTE: Display logo on screen:
    def _display_logo(self):
        print(f"""{Fore.LIGHTRED_EX}

                  ╔╦╗╦╔═╗╔═╗╔═╗╦═╗╔╦╗   ╔═╗╦ ╦╔╦╗╔═╗   ╦═╗╔═╗╔═╗╔═╗╔═╗╔╗╔╔╦╗╔═╗╦═╗
                   ║║║╚═╗║  ║ ║╠╦╝ ║║───╠═╣║ ║ ║ ║ ║───╠╦╝║╣ ╚═╗╠═╝║ ║║║║ ║║║╣ ╠╦╝
                  ═╩╝╩╚═╝╚═╝╚═╝╩╚══╩╝   ╩ ╩╚═╝ ╩ ╚═╝   ╩╚═╚═╝╚═╝╩  ╚═╝╝╚╝═╩╝╚═╝╩╚═
                                {Fore.LIGHTWHITE_EX}BY VXNET {Fore.LIGHTBLACK_EX}||| {Fore.LIGHTWHITE_EX}http://lefeu.nvnet.pl
                                          {Fore.YELLOW}Version: {Fore.LIGHTYELLOW_EX}{self.current_version}
                                  {Fore.LIGHTCYAN_EX}License valid until:{Fore.MAGENTA} {self.expiration_date}
        """)

        if self.current_version != self.latest_version:
            print(f"                          {Fore.LIGHTRED_EX}New update available! {Fore.LIGHTWHITE_EX}| {Fore.LIGHTMAGENTA_EX}{self.current_version} -> {self.latest_version}")
            print(f"                           {Fore.LIGHTYELLOW_EX}Download it from http://lefeu.nvnet.pl")

    def display_status_menu(self):
        print(f"{Fore.LIGHTYELLOW_EX}IMPORTANT: {Fore.LIGHTBLACK_EX}Configure auto responder before using it!")
        print(f"{Fore.YELLOW}HINT: {Fore.LIGHTBLACK_EX}Status is refreshing every {read_config()['MISCELLANEOUS']['refresh_status_after_seconds']} seconds. (You can change this in configutation page)")
        print(f"{Fore.YELLOW}HINT: {Fore.LIGHTBLACK_EX}You can edit account presence manually in {os.getcwd()}/DARconfig/presence.config.json")
        print(f"{Fore.YELLOW}HINT: {Fore.LIGHTBLACK_EX}You can disable hints in configuration page {Fore.GREEN}http://localhost:{read_config()['SERVER']['port']}/configuration")
        print(f"{Fore.RED}ERRORS: {Fore.LIGHTBLACK_EX}{State_AutoResponder.errors}") if State_AutoResponder.errors else None
        print(f"{Fore.RED}ERRORS: {Fore.LIGHTBLACK_EX}{State_Flask.errors}") if State_Flask.errors else None

        console = Console()
        
        table = Table(title="All processes status")
        table.add_column("Name", justify="left", style="cyan")
        table.add_column("Status", justify="left", style="yellow")
        table.add_column("Details", justify="left", style="purple")
        table.add_column("Info", justify="left", style="blue")
        
        # DISABLED / ERROR / SETUP REQUIRED / PENDING / OPERATING NORMALLY
        table.add_row("Control Panel",          State_Flask.status,                  f"Will be running on http://localhost:{read_config()['SERVER']['port']}",                                           "Web server for discord auto responder configuration.")
        table.add_row("Discord Auto Responder", State_AutoResponder.status,          f"Discord auto responder status please enter the http://localhost:{read_config()['SERVER']['port']} to configure.", "Discord Auto Responder Main Thread")

        console.print(table)

    def main(self):
        refresh_web_status_thread = Thread(target=refresh_web_status, daemon=True)
        refresh_web_status_thread.start()

        while True:
            self._clear_console()
            self._display_logo()
            self.display_status_menu()
            time.sleep(read_config()['MISCELLANEOUS']['refresh_status_after_seconds'])
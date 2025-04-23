# ----------------------------------------------------------------------------
#                            => CREDITS <=
# ----------------------------------------------------------------------------
#                 HACK: Developed and maintained by VXNET
#                        ✦ Do not copy code. ✦
#               ✦ Discord: https://discord.gg/HmGHGww2kY ✦
#                      Web: http://lefeu.nvnet.pl
# ----------------------------------------------------------------------------


import os

class Setup:
    def __init__(self) -> None:
        self.inputdir = "./DARconfig"
        self.configpath = os.path.join(f"DARconfig", "config.json")
        self.configpath_presence = os.path.join(f"DARconfig", "presence.config.json")
        # self.files = [
        #     f"./{self.inputdir}/logs.log",
        #     # f"./{self.inputdir}/addresses.txt",
        # ]
        self.default_config = """
{
    "license": "",
    "DISCORD_AUTO_RESPONDER": {
        "autostart": false,
        "token": "YOUR ACCOUNT TOKEN HERE",
        "responder_message": "Pong! Go to configuration page to set up custom message!"
    },
    "MISCELLANEOUS": {
        "refresh_status_after_seconds": 3.4,
        "enable_hints": true
    },
    "SERVER": {
        "port": 8844
    }
}
"""
#         self.presence_config = """
# {
#     "choose_random_online_status_from": ["online", "dnd", "idle", "invisible", "offline"],
#     "choose_random_activity_type_from": ["game", "streaming", "listening", "watching", "custom", "competing"],
#     "game": {
#         "name": "DAR"
#     },
#     "streaming": {
#         "name": "t.me/vxnetrip",
#         "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

#     },
#     "listening": {
#         "name": "Spotify"
#     },
#     "watching": {
#         "name": "DAR - Discord Auto Responder VXNET"
#     },
#     "custom": {
#         "name": "t.me/vxnetrip"
#     },
#     "competing": {
#         "name": "Tournament"
#     }
# } 
# """

    def writeJSON(self):
        if not os.path.exists(self.configpath):
            with open(self.configpath, "w+") as f:
                f.write(self.default_config)
    
    # def write_presenceJSON(self):
    #     if not os.path.exists(self.configpath):
    #         with open(self.configpath, "w+") as f:
    #             f.write(self.default_config)
    #     if not os.path.exists(self.configpath_presence):
    #         with open(self.configpath_presence, "w+") as f:
    #             f.write(self.presence_config)

    # def touchFiles(self):
    #     for filepath in self.files:
    #         if not os.path.exists(filepath):
    #             open(filepath, "w+").close()

    def run(self) -> None:
        if not os.path.exists(self.inputdir):
            os.mkdir(self.inputdir)
        # self.touchFiles()
        self.writeJSON()
        # self.write_presenceJSON()
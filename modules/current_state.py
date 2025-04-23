# ----------------------------------------------------------------------------
#                            => CREDITS <=
# ----------------------------------------------------------------------------
#                 HACK: Developed and maintained by VXNET
#                        ✦ Do not copy code. ✦
#               ✦ Discord: https://discord.gg/HmGHGww2kY ✦
#                      Web: http://lefeu.nvnet.pl
# ----------------------------------------------------------------------------

from asyncio.tasks import Task
from .utils import read_config

class State_AutoResponder:
    status = "OFF"
    process = None
    errors = []
    hints = []

class State_Flask:
    status = "OFF"
    errors = []
    hints = []

# ----------------------------------------------------------------------------
#                            => CREDITS <=
# ----------------------------------------------------------------------------
#                 HACK: Developed and maintained by VXNET
#                        ✦ Do not copy code. ✦
#               ✦ Discord: https://discord.gg/HmGHGww2kY ✦
#                      Web: http://lefeu.nvnet.pl
# ----------------------------------------------------------------------------

import time
import json
import websockets
import os
import re
import base64
import random
import tls_client
from datetime import datetime
from threading import Thread
from typing import List, Union, Dict, Tuple, Optional
from enum import Enum, IntEnum
from colorama import init as clinit
from websockets.asyncio.client import connect
from websockets.exceptions import ConnectionClosedError
import asyncio

from .current_state import State_AutoResponder
from .utils import read_config

clinit(autoreset=True)



class Status(Enum):
    "More information at https://discord.com/developers/docs/topics/gateway-events#activity-object-activity-types"
    ONLINE = "online"  # Online
    DND = "dnd"  # Do Not Disturb
    IDLE = "idle"  # AFK
    INVISIBLE = "invisible"  # Invisible and shown as offline
    OFFLINE = "offline"  # Offline

class Activity(Enum):
    "More information at https://discord.com/developers/docs/topics/gateway-events#activity-object"
    GAME = 0  #   Playing {name}
    STREAMING = 1  #   Streaming {details}
    LISTENING = 2  #   Listening to {name}
    WATCHING = 3  #   Watching {name}
    CUSTOM = 4  #   {emoji} {state} am cool
    COMPETING = 5  #   Competing in {name} World Champions

class OPCodes(Enum):
    "More information at https://discord.com/developers/docs/topics/opcodes-and-status-codes#opcodes-and-status-codes"
    Dispatch = 0  # An event was dispatched.
    Heartbeat = 1  # Fired periodically by the client to keep the connection alive.
    Identify = 2  # Starts a new session during the initial handshake.
    PresenceUpdate = 3  # Update the client's presence.
    VoiceStateUpdate = 4  # Used to join/leave or move between voice channels.
    Resume = 6  # Resume a previous session that was disconnected.
    Reconnect = 7  # You should attempt to reconnect and resume immediately.
    RequestGuildMembers = (
        8  # Request information about offline guild members in a large guild.
    )
    InvalidSession = 9  # The session has been invalidated. You should reconnect and identify/resume accordingly.
    Hello = (
        10  # Sent immediately after connecting, contains the heartbeat_interval to use.
    )
    HeartbeatACK = 11  # Sent in response to receiving a heartbeat to acknowledge that it has been received.
    RequestSoundboardSounds = 31 # 	Request information about soundboard sounds in a set of guilds.

class DiscordIntents(IntEnum):
    "More information at https://discord.com/developers/docs/topics/gateway#gateway-intents"
    GUILDS = 1 << 0
    GUILD_MEMBERS = 1 << 1
    GUILD_MODERATION = 1 << 2
    GUILD_EMOJIS_AND_STICKERS = 1 << 3
    GUILD_INTEGRATIONS = 1 << 4
    GUILD_WEBHOOKS = 1 << 5
    GUILD_INVITES = 1 << 6
    GUILD_VOICE_STATES = 1 << 7
    GUILD_PRESENCES = 1 << 8
    GUILD_MESSAGES = 1 << 9
    GUILD_MESSAGE_REACTIONS = 1 << 10
    GUILD_MESSAGE_TYPING = 1 << 11
    DIRECT_MESSAGES = 1 << 12
    DIRECT_MESSAGE_REACTIONS = 1 << 13
    DIRECT_MESSAGE_TYPING = 1 << 14
    MESSAGE_CONTENT = 1 << 15
    GUILD_SCHEDULED_EVENTS = 1 << 16
    AUTO_MODERATION_CONFIGURATION = 1 << 20
    AUTO_MODERATION_EXECUTION = 1 << 21


class Presence:
    """
    This class is used to manage the presence of a user on Discord.
    It allows you to set the user's online status and activities,
    which are displayed on the user's profile.

    Parameters:
    -----------
    online_status: Status
        An enum value representing the user's online status. This can be one of the predefined Status types, such as Online, Do Not Disturb, Away, Invisible, or Offline.

    Attributes:
    -----------
    online_status: Status
        The current online status of the user.
    activities: List[Activity]
        A list of activities that the user is currently engaged in. Each activity is represented by an Activity object, which contains information such as the name of the activity, its type, and any relevant URLs.

    Methods:
    --------
    addActivity(name: str, activity_type: Activity, url: Optional[str]) -> int
        Adds a new activity to the user's presence. Returns the index of the newly added activity.
    removeActivity(index: int) -> bool
        Removes an activity from the user's presence. Returns True if the activity was removed, False if the index was out of range.
    """

    def __init__(self, online_status: Status) -> None:
        self.online_status: Status = online_status
        self.activities: List[Activity] = []

    async def addActivity(
        self, name: str, activity_type: Activity, url: Optional[str]
    ) -> int:
        """
        Adds a new activity to the user's current presence in Discord.

        Parameters:
        ----------
        name : str
            The displayed name of the activity. This could also be the name of a game
        activity_type : Activity
            An enum value representing the type of activity. This should be one of the predefined Activity types, such as Playing, Streaming, Listening, etc.
        url : Optional[str]
            The URL associated with the activity. This is particularly relevant if the activity_type is Streaming, in which case this URL should be the link to the stream.

        Returns:
        -------
        int
            The index of the newly added activity in the activities list, which can be used to reference or modify the activity later.

        Example:
        -------
        >>> addActivity("Playing Chess", Activity.Playing)
        >>> addActivity("Streaming Art", Activity.Streaming, "http://twitch.tv/example_stream")

        Note:
        ----
        The URL parameter is only used if the activity_type is Streaming; for other activity types, the URL is ignored and can be omitted.

        """

        self.activities.append(
            {
                "name": name,
                "type": activity_type.value,  # The enum value of the activity type
                "url": url if activity_type == Activity.STREAMING else None,
            }
        )
        return len(self.activities) - 1


    async def removeActivity(self, index: int) -> bool:
        """
        Removes an activity to the user's current presence in Discord.

        Parameters
        ----------
        index : int
            The index of the activity to remove.

        Returns
        -------
        bool
            ``True`` if the activity was removed, ``False`` if the index was out of range.

        Example
        -------
        >>> removeActivity(0)
        >>> removeActivity(2)

        """

        if index < 0 or index >= len(self.activities):
            return False
        self.activities.pop(index)
        return True

class DiscordAPI:
    def __init__(self, token: str):
        self.token = token
        self.session = tls_client.Session(client_identifier="chrome_131")
        self.buildnumb = self.get_build_number()  # Get build number one time
        self.update_discord_cookies()

    def get_build_number(self):
        headers = {
            "Accept": "*/*",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Referer": "https://discord.com/login",
            "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"macOS"',
            "Sec-Fetch-Dest": "script",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        }

        def _extract_asset_files():
            request = self.session.get("https://discord.com/login", headers=headers)
            pattern = r'<script\s+src="([^"]+\.js)"\s+defer>\s*</script>'
            matches = re.findall(pattern, request.text)
            return matches

        try:
            files = _extract_asset_files()
            for file in files:
                build_url = f"https://discord.com{file}"
                response = self.session.get(build_url, headers=headers)
                if "buildNumber" not in response.text:
                    continue
                else:
                    build_number = response.text.split('build_number:"')[1].split('"')[0]
                    break

            return build_number
        except Exception as e:
            # print(f"Failed to get latest build number: {e}")
            return None


    def nonce(self) -> str:
        date = datetime.now()
        unixtx = time.mktime(date.timetuple())
        return str((int(unixtx)) * 1000 - 1420070400000)
    

    def update_discord_cookies(self) -> None:
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'sec-ch-ua': '"Brave";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'sec-gpc': '1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        }
        response = self.session.get('https://discord.com/', headers=headers)
        self.session.cookies.update(response.cookies)

    async def send_message(self, channel_id: int, content: str) -> None:
        URL = f"https://discord.com/api/v9/channels/{channel_id}/messages"

        self.session.headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'authorization': self.token,
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'origin': 'https://discord.com',
            'referer': f'https://discord.com/channels/@me/{channel_id}',
            'x-super-properties': self.build_x_super_properties(),
        }

        payload = {
            "mobile_network_type": "unknown",
            "content": content,
            "nonce": self.nonce(),
            "tts": False,
            "flags": 0
        }

        try:
            response = self.session.post(URL, json=payload)
            if response.status_code == 200:
                # print(f"Sent content of length {len(content)} to channel: {channel_id}")
                pass
            else:
                # print(f"Failed to send message: {response.text}")
                pass
        except Exception as e:
            # print(f"Error: {e}")
            pass

    def build_x_super_properties(self) -> str:
        props_str = f'{{"os":"Linux","browser":"Chrome","device":"","system_locale":"en-US","browser_user_agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36","browser_version":"131.0.0.0","os_version":"","referrer":"","referring_domain":"","referrer_current":"","referring_domain_current":"","release_channel":"stable","client_build_number":{self.buildnumb},"client_event_source":null,"has_client_mods":false}}'
        props_bytes = props_str.encode()
        props_encrypted = base64.b64encode(props_bytes)
        return props_encrypted.decode()





class DiscordWebSocket:
    def __init__(self) -> None:
        self.websocket_instance = None
        self.heartbeat_counter = 0
        self.username: str = None
        self.required_action: str = None
        self.heartbeat_interval: int = None
        self.last_heartbeat: float = None

    async def connect(self):
        self.websocket_instance = await connect(
            "wss://gateway.discord.gg/?v=10&encoding=json"
        )

    async def get_heartbeat_interval(self) -> None:
        resp: Dict = json.loads(await self.websocket_instance.recv())
        self.heartbeat_interval = resp["d"]["heartbeat_interval"]

    async def authenticate(self, token: str, rich: Presence) -> Union[Dict, bool]:
        await self.websocket_instance.send(
            json.dumps(
                {
                    "op": OPCodes.Identify.value,  # Operation code for Identify, used to authenticate the client to the server.
                    "d": {
                        "token": token,  # OAuth token used for verifying the client's identity with Discord.
                        "intents": DiscordIntents.DIRECT_MESSAGES
                                    | DiscordIntents.GUILD_MESSAGES
                                    | DiscordIntents.MESSAGE_CONTENT,  # Bitwise combination of intents specifying the types of events the client wants to receive.
                        "properties": {
                            "os": "linux",  # The operating system of the client
                            "browser": "Brave",  # The browser in which the client is running
                            "device": "Desktop",  # Type of device being used
                        },
                        # "presence": {
                        #     "activities": [activity for activity in rich.activities],  # List of activities for rich presence.
                        #     "status": rich.online_status.value,  # The client's online status (e.g., online, idle).
                        #     "since": time.time(),  # UNIX timestamp indicating when the client's status was last set.
                        #     "afk": False,  # Boolean flag indicating whether the client is marked as "away from keyboard" (AFK).
                        # },
                    },
                }
            )
        )
        try:
            resp = json.loads(await self.websocket_instance.recv())
            self.username = resp["d"]["user"]["username"]
            self.required_action = resp["d"].get("required_action")
            self.heartbeat_counter += 1
            self.last_heartbeat = time.time()
            return resp
        except Exception as e:
            return False

    async def send_heartbeat(self):
        await self.websocket_instance.send(
            json.dumps({"op": 1, "d": None})  # OPCodes.Heartbeat
        )
        self.heartbeat_counter += 1
        self.last_heartbeat = time.time()

    async def listen(self, token: str, activity: Presence = None):
        await self.connect()
        await self.get_heartbeat_interval()

        auth_resp = await self.authenticate(token, activity)
        if not auth_resp:
            # print("Failed to Authenticate")
            return

        # print(f"Authenticated {self.username} {self.required_action}")

        while True:
            try:
                State_AutoResponder.status = f"OPERATING NORMALLY {self.heartbeat_counter:04}"
                if time.time() - self.last_heartbeat >= self.heartbeat_interval / 1000 - 5:
                    # print(f"💓 Sending Heartbeat {self.heartbeat_counter:04}")
                    await self.send_heartbeat()

                incoming_message = await self.websocket_instance.recv()
                event_data = json.loads(incoming_message)

                if event_data["op"] == 0 and event_data["t"] == "MESSAGE_CREATE":
                    message_content = event_data["d"]["content"]
                    author = event_data["d"]["author"]["username"]
                    channel_id = event_data["d"]["channel_id"]
                    if "guild_id" not in event_data["d"] and author != self.username:
                        # print(f"📩 DM from {author}: {message_content}")
                        discordapi = DiscordAPI(token)
                        await discordapi.send_message(channel_id, read_config()['DISCORD_AUTO_RESPONDER']['responder_message'])
            except Exception as e:
                # print(f"Error: {e}")
                break






# Example usage
async def discord_auto_responder():
    State_AutoResponder.status = "LOADING"

    token = read_config()['DISCORD_AUTO_RESPONDER']['token']
    # enable_activities = read_config()['DISCORD_AUTO_RESPONDER']['enable_activities']
    
    # if enable_activities:

    #     presence_config = read_config("./DARconfig/presence.config.json")

    #     activity_types: List[Activity] = [
    #     Activity[x.upper()] for x in presence_config["choose_random_activity_type_from"]
    #     ]
    #     online_statuses: List[Status] = [
    #         Status[x.upper()] for x in presence_config["choose_random_online_status_from"]
    #     ]

    #     online_status = random.choice(online_statuses)
    #     chosen_activity_type = random.choice(activity_types)
    #     url = None

    #     match chosen_activity_type:
    #         case Activity.GAME:
    #             name = presence_config["game"]["name"]

    #         case Activity.STREAMING:
    #             name = presence_config["streaming"]["name"]
    #             url = presence_config["streaming"]["url"]

    #         case Activity.LISTENING:
    #             name = presence_config["listening"]["name"]

    #         case Activity.WATCHING:
    #             name = presence_config["watching"]["name"]

    #         case Activity.CUSTOM:
    #             name = presence_config["custom"]["name"]

    #         case Activity.COMPETING:
    #             name = presence_config["competing"]["name"]

    #     activity = Presence(online_status)
    #     await activity.addActivity(activity_type=chosen_activity_type, name=name, url=url)

    #     State_AutoResponder.status = "LOADED"

    #     socket = DiscordWebSocket()
    #     await socket.listen(token, activity)

    # else:
    State_AutoResponder.status = "LOADED"

    socket = DiscordWebSocket()
    await socket.listen(token)
        
        
if __name__ == "__main__":
    asyncio.run(discord_auto_responder())
"""
Core module of discord bot, it connects, keeps alive, get messages and send
messages.

Args:
    token: Discord bot token.
    logger: An instance of the logging module.
"""

import json
from time import sleep
from threading import Thread

import requests
import websocket


class Messenger:
    """
    Core module of discord bot, it connects, keeps alive, get messages and send
    messages.

    Args:
        token: Discord bot token.
        logger: An instance of the logging module.
    """

    infos = {'message':        None,
             'channel_id':     None,
             'message_id':     None,
             'guild_id':       None,
             'reaction_added': None,
             'seq':            0,
             'session_id':     None}

    author = {'username': 'VTBot',
              'id': "948058941668069386"}
    api_endpoint = "https://discord.com/api/v9"
    url = "wss://gateway.discord.gg/?v=9&encoding=json"
    attachments = []

    def __init__(self, token, logger):
        """
        Core module of discord bot, it connects, keeps alive, get messages and
        send messages.

        Args:
            token: Discord bot token.
            logger: An instance of the logging module.
        """

        self.token = token
        self.log = logger.log

        self.heartbeat_interval = 42
        self.web_socket = websocket.WebSocket()

    def __get_message(self):
        """
        Gets the messages (event) sent by discord.

        Args:
            None

        Returns:
            Dictionnary: The event sent by discord.
        """

        try:
            message = self.web_socket.recv()
            if message:
                return json.loads(message)
            return {}
        except websocket.WebSocketConnectionClosedException as socket_error:
            self.log('error', f"Socket error : {socket_error}")
            self.reconnect()
            return None

    def get_reaction_added(self) -> str:
        """
        Returns the last reaction.

        Args:
            None

        Returns:
            String: The last reaction added.
        """

        return self.infos['reaction_added']

    def set_reaction_added(self, reaction):
        """
        Sets the last reaction added.

        Args:
            reaction: The reaction to set.

        Returns:
            None
        """

        self.infos['reaction_added'] = reaction

    def send_reaction(self, channel_id, message_id, reaction):
        """
        Sends a reaction to a message.

        Args:
            channel_id: The id of the channel the message to react
                        is located in.
            message_id: The id of the message to react to.
            reaction: The reaction to add.

        Returns:
            None
        """

        headers = {
            "Authorization": f"Bot {self.token}",
            "Content-Type":  "Application/json"
        }

        req = requests.put(
                            url=f"{self.api_endpoint}/channels/{channel_id}" +
                            f"/messages/{message_id}/reactions/{reaction}/@me",
                            headers=headers)
        self.log('trace',
                 f"Status code : {req.status_code}\nText : {req.text}")
        if req.status_code == 429:
            self.log('error', "Rate limited")
            sleep(0.5)
            self.log('debug', "Re-sending")
            self.send_reaction(channel_id, message_id, reaction)
        elif req.status_code != 204:
            self.log('error', "An error as occured")
            self.log('error',
                     f"Status code : {req.status_code}\nText : {req.text}")

    def send_embed(
        self,
        channel_id,
        embed_params,
        guild_id=None,
        message_id=None
    ):
        """
        Sends an embeded message.

        Args:
            channel_id: The id of the channel to send the message in.
            embed_params: The necessary parameters for an embeded message.
            e.g: embed_params = {
                    'title': 'foo',
                    'description': 'bar',
                    'color': int,
                    'fields': [{'name': 'Name of field 1', 'value': 'value'},
                               {'name': 'Name of field n', 'value': 'value'}]
                    }
            guild_id (Optional): The id of the guild the message is located in.
            message_id (Optional): The id of the message to respond to

        Returns:
            None
        """

        headers = {
            "Authorization": f"Bot {self.token}",
            "Content-Type":  "Application/json"
        }

        fields = [{'name': field['name'], 'value': field['value']}
                  for field in embed_params['fields']]
        payload = {
              "content": "",
              "embed": {
                "title": embed_params['title'],
                "url": "",
                "description": embed_params['description'],
                "color": embed_params['color'],
                "fields": fields
                }
            }

        if message_id and guild_id:
            payload['message_reference'] = {
                "guild_id": guild_id,
                "message_id": message_id
                }

        request = requests.post(
            url=f"{self.api_endpoint}/channels/{channel_id}/messages",
            headers=headers, json=payload)
        self.status_code_checker(request)

    def send_files(
        self,
        channel_id: str,
        files: list
    ):
        """
        Sends a file (cannot respond to a message).

        Args:
            channel_id: The id of the channel to send the message in.
            files: List of file paths.

        Returns:
            None
        """

        attachments_headers = {
            "Authorization": f"Bot {self.token}"
        }

        payload = []
        files_dict = {}
        for index, file in enumerate(files):
            filename = file.split("/")[-1]
            payload.append({
                'Content-Disposition': 'form-data; ' +
                f'name="file{index}"; filename="{filename}"',
                'Content-Type': 'image/png',
            })
            with open(file, 'rb') as file:
                files_dict[f"file{index}"] = \
                    (filename, file.read(), 'image/png')
        request = requests.post(
            url=f"{self.api_endpoint}/channels/{channel_id}/messages",
            headers=attachments_headers, data=payload, files=files_dict)
        self.status_code_checker(request)

    def status_code_checker(self, request):
        """
        Checks if the HTTP code received indicates a success or not.

        Args:
            request: the reponse from your HTTP request

        Returns:
            Boolean: True if the status code is 200
        """

        if request.status_code != 200:
            self.log('trace',
                     f"req status code: {request.status_code}" +
                     f"\nreq text: {request.text}\nHeaders: {request.headers}")
        return request.status_code == 200

    def get_all_channels(self, guild_id):

        headers = {
            "Authorization": f"Bot {self.token}",
            "Content-Type":  "Application/json"
        }
        request = requests.get(
            url=f"{self.api_endpoint}/guilds/{guild_id}/channels",
            headers=headers)
        return request.text


    def get_messages(self, channel_id):

        headers = {
            "Authorization": f"Bot {self.token}",
            "Content-Type":  "Application/json"
        }
        request = requests.get(
            url=f"{self.api_endpoint}//channels/{channel_id}/messages",
            headers=headers)
        return request.text

    def send_message(
        self,
        channel_id,
        message,
        guild_id=None,
        message_id=None
    ):
        """
        Sends an classic message.

        Args:
            channel_id: The id of the channel to send the message in.
            embed_params: The necessary parameters for an embeded message.
            message: A string to send as a message.
            guild_id (Optional): The id of the guild the message is located in.
            message_id (Optional): The id of the message to respond to

        Returns:
            None
        """

        headers = {
            "Authorization": f"Bot {self.token}",
            "Content-Type":  "Application/json"
        }

        payload = {"channel_id": channel_id,
                   "content": message}

        if message_id and guild_id:
            payload['message_reference'] = {
                "guild_id": guild_id,
                "message_id": message_id
                }

        request = requests.post(
            url=f"{self.api_endpoint}/channels/{channel_id}/messages",
            headers=headers, json=payload)
        self.status_code_checker(request)

    def __heartbeat(self):
        """
        Loops to send heartbeats (to keep the bot alive).

        Args:
            None

        Returns:
            None
        """

        self.log('debug', "Heartbeat started")
        while True:
            self.__send_heartbeat()
            sleep(self.heartbeat_interval)

    def __send_heartbeat(self):
        """
        Sends a heartbeat.

        Args:
            None

        Returns:
            None
        """

        heartbeat_json = {"op": 1,
                          "d": "null"}

        self.web_socket.send(json.dumps(heartbeat_json))
        self.log('debug', "Heartbeat sent")

    def get_author_username(self) -> str:
        """
        Returns the username of the Author.

        Args:
            None

        Returns:
            String: Username of the author of the last message.
        """

        return self.author['username']

    def get_author_id(self) -> str:
        """
        Returns the id of the Author.

        Args:
            None

        Returns:
            String: Id of the author of the last message.
        """

        return self.author['id']

    def get_message(self) -> str:
        """
        Returns the last message.

        Args:
            None

        Returns:
            String: Last message received.
        """

        return self.infos['message']

    def get_channel_id(self):
        """
        Returns the username of the Author.

        Args:
            None

        Returns:
            String: Username of the author of the last message.
        """

        return self.infos['channel_id']

    def get_attachments(self) -> list:
        """
        Returns the attachments of the last message.

        Args:
            None

        Returns:
            List: List of the attachments of the last message.
        """

        return self.attachments

    def get_message_id(self) -> str:
        """
        Returns the id of the last message.

        Args:
            None

        Returns:
            String: Id of the last message.
        """

        return self.infos['message_id']

    def get_guild_id(self) -> str:
        """
        Returns the guild id of the last message.

        Args:
            None

        Returns:
            String: Id of the last message.
        """

        return self.infos['guild_id']

    def __get_all_infos(self, event):
        """
        Retreives all of the informations of a givent event.

        Args:
            event: Event received from Discord.

        Returns:
            None
        """
        if event:
            if event['t'] == "MESSAGE_CREATE":
                self.author = event['d']['author']
                self.infos['message'] = event['d']['content']
                self.infos['channel_id'] = event['d']['channel_id']
                self.attachments = event['d']['attachments']
                self.infos['message_id'] = event['d']['id']
                self.infos['guild_id'] = event['d']['guild_id']
                self.log('debug',
                        f"{self.author['username']} : {self.infos['message']}")
            elif event['t'] == "READY":
                servers_list = {}
                messages_list = {}
                for guild in event['d']['guilds']:
                    channels = json.loads(self.get_all_channels(guild['id']))
                    channels_list = []
                    for channel in channels:
                        id = channel['id']
                        name = channel['name']
                        channels_list.append({"id": id, "name": name})
                        messages = json.loads(self.get_messages(channel['id']))
                        messages_temp = []
                        for message in messages:
                            if type(message) == dict and (("code" in message.keys() and message['code'] != 50001) or "code" not in message.keys()):
                                author = message['author']['username']
                                content = message['content']
                                timestamp = message['timestamp']
                                messages_temp.append({"author": author, "content": content,"date": timestamp})
                        messages_list[guild['id']] = {channel['id']: messages_temp}
                    servers_list[guild['id']] = {"server_name": "test", "channels": channels_list}
                with open("interface/servers.json", 'w', encoding="UTF-8") as file:
                    json.dump(servers_list, file)
                with open("interface/messages.json", 'w', encoding="UTF-8") as file:
                    json.dump(messages_list, file)
                self.log('none', "READY")
            if event['s'] is not None:
                self.infos['seq'] = event['s']

    def __connect(self):
        """
        Connects the bot to the discord websocket.

        Args:
            None

        Returns:
            None
        """

        self.log('none', "Connecting")
        self.web_socket.connect(self.url)
        event = self.__get_message()
        if event is None:
            self.reconnect()
        else:
            self.heartbeat_interval = event['d']['heartbeat_interval'] / 1000
            self.log('none', f"Heartbeat interval : {self.heartbeat_interval}")
            self.log('none', "Connected")

    def reconnect(self):
        """
        Reconnects to the Discord websocket (can be bacause the connection
        was lost or if a op code 7 is received).

        Args:
            None

        Returns:
            None
        """

        self.log("debug", "Reconnecting")
        self.web_socket.close()
        self.log("trace", "Connectiong closed")
        self.__connect()

        payload = {
          "op": 6,
          "d": {
            "token": self.token,
            "session_id": self.infos['session_id'],
            "seq": self.infos['seq']
          }
        }

        self.web_socket.send(json.dumps(payload))
        message = self.__get_message()
        self.__op_code_treatment(message)
        self.log('debug', "Reconnected")

    def __identify(self):
        """
        Identifies the bot.

        Args:
            None

        Returns:
            None
        """

        payload = {
          "op": 2,
          "d": {
            "token": self.token,
            "intents": 1544,
            "properties": {
                "$os": "linux",
                "$browser": "VTBot",
                "$device": "VTBot"
            }
          }
        }

        self.web_socket.send(json.dumps(payload))
        message = self.__get_message()
        self.__op_code_treatment(message)

    def __core(self):
        """
        Core of the discord bot gets the messages and sends them to
        op_code_treatment() or get_all_infos() (while True loop).

        Args:
            None

        Returns:
            None
        """

        while True:
            try:
                event = self.__get_message()
            except websocket.WebSocketConnectionClosedException as so_error:
                self.log('debug', "Help, I'm dying" +
                         f"Exception: {so_error}")
                self.reconnect()
            try:
                self.__op_code_treatment(event)
            except KeyError as error:
                self.log('error', f"key not found error : {error}")

    def __op_code_treatment(self, event):
        """
        Handles the op codes received.

        Args:
            event: event received by discord.

        Returns:
            None
        """

        if event is not None:
            op_code = event['op']
            self.log('trace', event)
            if op_code == 11:
                self.log("debug", "heartbeat recieved")
                self.log('trace', f"event : {event}")
            elif op_code == 9:
                self.log('debug', "Re-identifying")
                self.log('trace', f"event : {event}")
                self.__identify()
            elif op_code == 7:
                self.log('debug', "op code 7 received")
                self.reconnect()
            elif op_code == 0:
                if event['t'] == "GUILD_CREATE":
                    pass
                elif event['t'] == "READY":
                    self.infos['session_id'] = event['d']['session_id']
                    self.log('trace', f"event : {event}")
                elif event['t'] == "MESSAGE_REACTION_ADD":
                    self.__reaction_handling(event['d'])
            elif op_code == 1:
                self.__send_heartbeat()
                self.log('trace', f"event : {event}")
            self.__get_all_infos(event)

    def __reaction_handling(self, data):
        """
        Handles the reactions to message.

        Args:
            data: event['d'] received by discord

        Returns:
            None
        """

        self.log('trace', f"emoji received {data['emoji']['name']}")
        self.infos['reaction_added'] = data['emoji']['name']

    def set_message(self, message):
        """
        Sets the last message received

        Args:
            message: message to be set

        Returns:
            None
        """

        self.infos['message'] = message

    def start(self):
        """
        Entrypoint of the class, starts the bot.

        Args:
            None

        Returns:
            None
        """

        self.__connect()
        # threading._start_new_thread(self.__heartbeat, ())
        heart = Thread(target=self.__heartbeat)
        heart.start()

        self.__identify()

        # threading._start_new_thread(self.__core, ())
        start_core = Thread(target=self.__core)
        start_core.start()

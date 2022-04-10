import requests
import json
from time import sleep
import sys
from random import randint

import websocket
import threading


class Messenger:

    def __init__(self, TOKEN, logger):
        self.TOKEN = TOKEN
        self.api_endpoint = "https://discord.com/api/v9"
        self.url = "wss://gateway.discord.gg/?v=9&encoding=json"
        self.HEADERS = {
            "Authorization" : f"Bot {TOKEN}",
            "Content-Type" : "Application/json"
        }
        self.ATTACHMENTS_HEADERS = {
            "Authorization" : f"Bot {TOKEN}"
        }
        self.ws = websocket.WebSocket()
        self.message = ""
        self.channelId = ""
        self.message_id = ""
        self.guild_id = ""
        self.author = {'username' : 'VTBot',
                        'id' : "948058941668069386"}
        self.attachments = []
        self.log = logger.log
        self.seq = 0
        self.session_id = ""
        self.reaction_added = None

    def get_message(self):
        message = self.ws.recv()
        if message:
            return json.loads(message)

    def get_reaction_added(self):
        return self.reaction_added

    def set_reaction_added(self, reaction):
        self.reaction_added = reaction

    def send_reaction(self, channel_id, message_id, reaction):
        req = requests.put(
        url = f"{self.api_endpoint}/channels/{channel_id}/messages/{message_id}/reactions/{reaction}/@me",
        headers = self.HEADERS)
        self.log('trace', f"Status code : {req.status_code}\nText : {req.text}")
        if req.status_code == 429:
            self.log('error', "Rate limited")
            sleep(0.5)
            self.log('debug', "Re-sending")
            self.send_reaction(channel_id, message_id, reaction)
        elif req.status_code != 204:
            self.log('error', "An error as occured")
            self.log('error', f"Status code : {req.status_code}\nText : {req.text}")


    def send_message(
        self,
        channel_id,
        message,
        guild_id = None,
        message_id = None,
        embed = False,
        embed_params = None,
        files = None
    ):

        payload = {"channel_id": channel_id,
                "content": message}

        if message_id and guild_id:
            payload['message_reference'] = {
                "guild_id": guild_id,
                "message_id": message_id
                }

        if embed and embed_params:

            fields = [{'name' : field['name'], 'value' : field['value']} for field in embed_params['fields']]
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

            req2 = requests.post(
                url=f"{self.api_endpoint}/channels/{channel_id}/messages",
                headers=self.HEADERS, json=payload)

        elif files:
            payload = []
            files_dict = {}
            for index, file in enumerate(files):
                filename = file.split("/")[-1]
                payload.append({
                    'Content-Disposition': 'form-data; ' + \
                    f'name="file{index}"; filename="{filename}"',
                    'Content-Type': 'image/png',
                })
                files_dict[f"file{index}"] = open(file, 'rb')
            req2 = requests.post(
                url=f"{self.api_endpoint}/channels/{channel_id}/messages",
                headers=self.ATTACHMENTS_HEADERS, data = payload, files = files_dict)
        else:
            req2 = requests.post(
                url=f"{self.api_endpoint}/channels/{channel_id}/messages",
                headers=self.HEADERS, json=payload)
        if req2.status_code != 200:
            self.log('trace',
            f"req status code : {req2.status_code}" + \
            f"\nreq text : {req2.text}\nHeaders : {req2.headers}")

    def heartbeat(self):
        self.log('debug', "Heartbeat started")
        while True:
            self.send_heartbeat()
            sleep(self.heartbeat_interval)

    def send_heartbeat(self):
        heartbeat_JSON = {
        "op" : 1,
        "d" : "null"
        }

        self.ws.send(json.dumps(heartbeat_JSON))
        self.log('debug', "Heartbeat sent")



    def getAuthorUsername(self):
        return self.author['username']

    def getAuthorId(self):
        return self.author['id']

    def getMessage(self):
        return self.message

    def getChannelId(self):
        return self.channelId

    def getAttachments(self):
        return self.attachments

    def getMessageId(self):
        return self.message_id

    def getGuildId(self):
        return self.guild_id

    def get_all_infos(self, event):
        if event['t'] == "MESSAGE_CREATE":
            self.author = event['d']['author']
            self.message = event['d']['content']
            self.channelId = event['d']['channel_id']
            self.attachments = event['d']['attachments']
            self.message_id = event['d']['id']
            self.guild_id = event['d']['guild_id']
            self.log('debug', f"{self.author['username']} : {self.message}")
        if event['s'] != None:
            self.seq = event['s']

    def connect(self):
        self.log('none', "Connecting")
        self.ws.connect(self.url)
        event = self.get_message()
        self.heartbeat_interval = event['d']['heartbeat_interval'] / 1000
        self.log('none', f"Heartbeat interval : {self.heartbeat_interval}")
        self.log('none', "Connected")

    def reconnect(self):
        self.log("debug", "Reconnecting")
        self.ws.close()
        self.log("trace", "Connectiong closed")
        self.connect()

        payload = {
          "op": 6,
          "d": {
            "token": self.TOKEN,
            "session_id": self.session_id,
            "seq": self.seq
          }
        }

        self.ws.send(json.dumps(payload))
        message = self.get_message()
        self.op_code_treatment(message)
        self.get_all_infos(message)
        self.log('debug', "Reconnected")

    def identify(self):
        payload = {
          "op": 2,
          "d": {
            "token": self.TOKEN,
            "intents": 1544,
            "properties" : {
                "$os" : "linux",
                "$browser" : "VTBot",
                "$device" : "VTBot"
            }
          }
        }

        self.ws.send(json.dumps(payload))
        message = self.get_message()
        self.op_code_treatment(message)
        self.get_all_infos(message)

    def core(self):
        while True:
            try:
                event = self.get_message()
            except:
                self.send_message(self.channelId, "Help, I'm dying")
                self.log('debug', "Help, I'm dying")
                self.reconnect()
            try :
                self.op_code_treatment(event)
                self.get_all_infos(event)
            except:
                pass

    def op_code_treatment(self, event): # A faire get_all_infos from op_code_treatment
        op_code = event['op']
        self.log('trace', event)
        if op_code == 11:
            self.log("debug", "heartbeat recieved")
            self.log('trace', f"event : {event}")
        elif op_code == 9:
            self.log('debug', "Re-identifying")
            self.log('trace', f"event : {event}")
            self.identify()
        elif op_code == 7:
            self.log('debug', "op code 7 received")
            self.reconnect()
        elif op_code == 0:
            if event['t'] == "GUILD_CREATE":
                pass
            elif event['t'] == "READY":
                self.session_id = event['d']['session_id']
                self.log('trace', f"event : {event}")
                self.send_message("956409767591542794", "READY", "946241187080187934", message_id = "961823986621231165")
            elif event['t'] == "MESSAGE_REACTION_ADD":
                self.reaction_handling(event['d'])
                self.get_all_infos(event)
        elif op_code == 1:
            self.send_heartbeat()
            self.log('trace', f"event : {event}")
        self.get_all_infos(event)

    def reaction_handling(self, data):
        self.log('trace', f"emoji received {data['emoji']['name']}")
        self.reaction_added = data['emoji']['name']

    def start(self):
        self.connect()
        threading._start_new_thread(self.heartbeat, ())

        self.identify()

        threading._start_new_thread(self.core, ())

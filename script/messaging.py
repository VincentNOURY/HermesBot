import requests
import json
from time import sleep
import sys

import websocket
import threading


class Messenger:

    def __init__(self, TOKEN, logger):
        self.TOKEN = TOKEN
        self.url = "wss://gateway.discord.gg/?v=9&encoding=json"
        self.HEADERS = {
            "Authorization" : f"Bot {TOKEN}",
            "Content-Type" : "Application/json"
        }
        self.ws = websocket.WebSocket()
        self.message = ""
        self.channelId = ""
        self.author = {'username' : 'VTBot',
                        'id' : "948058941668069386"}
        self.attachments = []
        self.log = logger.log()

    def get_message(self):
        message = self.ws.recv()
        if message:
            return json.loads(message)

    def send_message(self, channel_id, message):
        data = {"content": message}
        req2 = requests.post(
                url=f"https://discord.com/api/channels/{channel_id}/messages",
                headers=self.HEADERS, json=data)

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

    def get_all_infos(self, event):
        self.author = event['d']['author']
        self.message = event['d']['content']
        self.channelId = event['d']['channel_id']
        self.attachments = event['d']['attachments']
        self.log('debug', f"{self.author['username']} : {self.message}")

    def connect(self):
        sys.stdout.write("## Connecting ##\n")
        self.ws.connect(self.url)
        event = self.get_message()
        self.heartbeat_interval = event['d']['heartbeat_interval'] / 1000
        self.log('none', f"Heartbeat interval : {self.heartbeat_interval}")
        threading._start_new_thread(self.heartbeat, ())
        self.log('none', "Connected")

    def reconnect(self):
        pass


    def core(self):
        while True:
            try:
                event = self.get_message()
            except:
                self.send_message(self.channelId, "Help, I'm dying")
                sys.stdout.write("Help, I'm dying\n")
                self.reconnect()
            try :
                self.get_all_infos(event)
            except:
                pass

    def op_code_treatment(self, event):
        op_code = event['op']
        if op_code == 11:
            self.log("debug", "heartbeat recieved")
        elif op_code == 1:
            self.send_heartbeat()

    def start(self):
        self.connect()

        payload = {
          "op": 2,
          "d": {
            "token": self.TOKEN,
            "intents": 513,
            "properties" : {
                "$os" : "linux",
                "$browser" : "VTBot",
                "$device" : "VTBot"
            }
          }
        }

        self.ws.send(json.dumps(payload))
        threading._start_new_thread(self.core, ())

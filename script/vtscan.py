import requests
import json
from os.path import exists
from os import remove
import threading
from time import sleep

class Vtscan:

    def __init__(self, api_key, messenger, url, channel_id, message_id, guild_id):
        self.api_key = api_key
        self.channel_id = channel_id
        self.messenger = messenger
        self.message_id = message_id
        self.guild_id = guild_id
        self.file_path = ""
        self.url = url

    def virus_total_api_calls(self):
        api_post_light = "https://www.virustotal.com/api/v3/files"
        header = {'x-apikey' : self.api_key}
        files = {'file' : (self.file_path, open(self.file_path, 'rb'))}
        post_request = requests.post(api_post_light, headers = header, files = files)
        if post_request.status_code == 429:
            self.messenger.send_message(channel_id, "VirusTotal rate limited sorry")
            self.log('error', "VirusTotal rate limited")
            raise
        elif post_request.status_code != 200:
            self.log('error', f"Status code {post_request.status_code} received, {post_request.text}")
            raise
        dict = post_request.json()['data']
        id = dict['id']

        analyses_link = "https://www.virustotal.com/api/v3/analyses/" + id
        sleep(1)

        get_request = requests.get(analyses_link, headers = header)
        new_dict = get_request.json()['data']['attributes']

        while new_dict['status'] != "completed":
            print("waiting more")
            sleep(69)
            get_request = requests.get(analyses_link, headers = header)
            new_dict = get_request.json()['data']['attributes']

        Keys = new_dict['results'].keys()

        bool = False

        for key in Keys:
            temp = new_dict['results'][key]['category']
            if temp in ["suspicious", "malicious"]:
                self.messenger.send_message(self.channel_id, f"❌⚠️🚫🚫 Malicious file {self.file_path} detected !", self.message_id, self.guild_id)
                self.messenger.send_message(self.channel_id, f"Reported by : {key}", self.message_id, self.guild_id)
                bool = True
        if not bool:
            self.messenger.send_message(self.channel_id, f"File {self.file_path} is safe !", self.message_id, self.guild_id)
        remove(self.file_path)

    def scan(self):
        req = requests.get(self.url, allow_redirects=True)
        self.file_path = f"scan/temp_file_{self.url.split('/')[-1]}"
        i = 0
        while exists(self.file_path):
            temp = self.file_path.split(".")
            self.file_path = '.'.join(temp[0:-1]) + str(i) + "." + temp[-1]
            i += 1
        if "." not in self.file_path:
            self.file_path = self.file_path.split(".")[-1]
        open(self.file_path, 'wb').write(req.content)

        self.virus_total_api_calls()
        #thread = threading.Thread(target=self.virus_total_api_calls)
        #thread.start()
        #virus_total_api_calls(api_key, name, channel_id)

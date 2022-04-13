"""
vtscan module is the virus scanning module for discord bot, it uses the
VirusTotal api to scan the files.

Args:
    channel_id: Id of the channel to send the response
                and for the shopping list
    author_id: Ensures that only the one that requested the removal
               of an item can remove it

"""

from time import sleep
from os import remove, path
import requests


class Vtscan:
    """
    vtscan module is the virus scanning module for discord bot, it uses the
    VirusTotal api to scan the files.

    Args:
        channel_id: Id of the channel to send the response
                    and for the shopping list
        author_id: Ensures that only the one that requested the removal
                   of an item can remove it

    """

    def __init__(self,
                 api_key: str,
                 # messenger,
                 logger,):
        """
        Initialization of the Vtscan module

        Args:
            channel_id: Id of the channel to send the response
                        and for the shopping list
            author_id: Ensures that only the one that requested the removal
                       of an item can remove it

        """
        self.api_key = api_key
        # self.channel_id = None
        # self.messenger = messenger
        # self.message_id = None
        # self.guild_id = None
        # self.url = url
        self.log = logger.log

    def send_file_request(self, file_path):
        """
        Sends the VirusTotal API a request with the file

        Args:
            file_path: path of the file

        Returns:
            post_request: The result of the request
        """

        api_post_light = "https://www.virustotal.com/api/v3/files"
        header = {'x-apikey': self.api_key}
        with open(file_path, 'rb') as file:
            files = {'file': (file_path, file.read())}
        return requests.post(api_post_light, headers=header, files=files)

    def status_code_treatment(self, status_code, text):
        """
        Verifies the HTTP code received

        Args:
            status_code: HTTP code of the request made
            text:        Text received from the request (used for logs)

        Returns:
            new_dict: Dictionnary of the result for the file
        """

        if status_code == 429:
            # self.messenger.send_message(self.channel_id,
            #                             "VirusTotal rate limited sorry")
            self.log('error', "VirusTotal rate limited")
            return "VirusTotal rate limited sorry"
        if status_code != 200:
            message = f"Status code {status_code} received, {text}"
            self.log('error', message)
            return message
        return ""

    def file_treated_checker(self, analyse_id):
        """
        Calls the VirusTotal API, retreives the status of the checked file

        Args:
            analyse_id: Id of the analysed file (retreived from the previous
                        call to the VirusTotal API)

        Returns:
            new_dict: Dictionnary of the result for the file
        """

        link = f"https://www.virustotal.com/api/v3/analyses/{analyse_id}"
        header = {'x-apikey': self.api_key}

        get_request = requests.get(link, headers=header)
        new_dict = get_request.json()['data']['attributes']

        while new_dict['status'] != "completed":
            self.log("debug", "waiting more")
            sleep(69)
            get_request = requests.get(link, headers=header)
            new_dict = get_request.json()['data']['attributes']

        return new_dict

    def virus_total_api_calls(self, file_path):
        """
        Calls the VirusTotal API, retreives the status and sends a message

        Args:
            None

        Returns:
            None
        """

        post_request = self.send_file_request(file_path)

        status = self.status_code_treatment(post_request.status_code,
                                            post_request.text)
        if status:
            return status

        analyse_id = post_request.json()['data']['id']

        new_dict = self.file_treated_checker(analyse_id)

        keys = new_dict['results'].keys()

        file_is_safe = True

        for key in keys:
            temp = new_dict['results'][key]['category']
            if temp in ["suspicious", "malicious"]:
                message = f"❌⚠️🚫🚫 Malicious file {file_path} detected !"
                # self.messenger.send_message(self.channel_id, message,
                #                             self.message_id, self.guild_id)
                message += f"\nReported by : {key}"

                # self.messenger.send_message(self.channel_id,
                #                             f"Reported by : {key}",
                #                             self.message_id,
                #                             self.guild_id)

                file_is_safe = False
        if file_is_safe:
            message = f"File {file_path} is safe !"
            # self.messenger.send_message(self.channel_id,
            #                             f"File {file_path} is safe !",
            #                             self.message_id,
            #                             self.guild_id)

        remove(file_path)
        return message

    def scan(self,
             url: str) -> str:
        """
        Entry for the scanning process (calls virus_total_api_calls())

        Args:
            None

        Returns:
            None
        """

        req = requests.get(url, allow_redirects=True)
        file_path = f"scan/temp_file_{url.split('/')[-1]}"
        i = 0
        while path.exists(file_path):
            temp = file_path.split(".")
            file_path = '.'.join(temp[0:-1]) + str(i) + "." + temp[-1]
            i += 1
        if "." not in file_path:
            file_path = file_path.split(".")[-1]
        with open(file_path, 'wb') as file:
            file.write(req.content)

        return self.virus_total_api_calls(file_path)

import requests
import json
from time import sleep
from threading import Thread
from os import cpu_count

from messaging import Messenger
from shopping_list import Shopping_list
from vtscan import Vtscan
from writer import Writer
from logger import Logger
from read_conf import Conf



def help_message(channel_id):
    help_message = """Commands you can use are :
!help   : For help.
!test   : Test if the bot is available
!scan   : With a file attached it scans the file for viruses and send the results back
!clear  : To clear your shopping list
!add    : To add an item to your shopping list (!add item)
!create : To create a shopping list for this channel
!see    : To see your shopping list
!remove : To remove an item from the shopping list"""
    messenger.send_message(channel_id, help_message)


def main():
    message = messenger.getMessage().lower()
    channel_id = messenger.getChannelId()
    #print(message)
    author = messenger.getAuthorUsername()
    author_id = messenger.getAuthorId()
    message_id = messenger.getMessageId()
    guild_id = messenger.getGuildId()
    bot_id = "948058941668069386"

    if "<@!" in message:
        pass
    elif message == "!test":
        messenger.send_message(channel_id, "Test sucessful !")

    elif message == "!help":
        help_message(channel_id)

    elif message == "!scan":
        attachments = messenger.getAttachments()
        if len(attachments) == 0:
            messenger.send_message(channel_id, "Please add a file to scan.")
        else:
            messenger.send_message(channel_id, "Scanning ...", message_id, guild_id)
            threads_list = []
            for i in range(len(attachments)):
                threads_list.append(Thread(target=Vtscan(conf["Vt_api_key"], messenger, attachments[i]["url"], channel_id, message_id, guild_id).scan))
            [thread.start() for thread in threads_list]

    elif message == "!create":
        shopping_list.create_shopping_list(channel_id)

    elif message == "!clear":
        shopping_list.clear_shopping_list(channel_id)

    elif "!add" in message and author_id != bot_id:
        if shopping_list.verify_shopping_list_exists(channel_id):
            if len(message[5:]) < 1:
                messenger.send_message(channel_id, "Usage !add item")
            else:
                shopping_list.add_to_shopping_list(channel_id, message)
        else:
            messenger.send_message(channel_id, "There is no shopping list created for this channel.")

    elif message == "!see":
        shopping_list.see_shopping_list(channel_id)
    elif message == "!remove":
        shopping_list.delete_from_shopping_list(channel_id, author_id)
    elif message == "<@!948058941668069386>":
        messenger.send_message(channel_id, "Yes, it's me.")
    else:
        if message and "!" == message[0] and author_id != bot_id:
            messenger.send_message(channel_id, "Unknown command.")


def set_status():
    pass

if __name__ == '__main__':
    logger = Logger('trace')
    conf = Conf("config/config.json").load()
    logger.log('special', '\n\n\n\n\n')
    writer = Writer("shopping_list/shopping_list.json")
    messenger = Messenger(conf['Discord_token'], logger)
    messenger.start()
    shopping_list = Shopping_list(messenger, writer)

    while True:
        main()
        sleep(0.3)

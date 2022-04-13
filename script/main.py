"""
This is the main module used to control the main logic of the bot reponses.

Functions :
    send_help_message(channel_id)
    movie_search(search, channel_id, guild_id=None, message_id=None)
    main()
    set_status() : Not implemented yet
"""


from time import sleep
from save_thread_result import ThreadWithResult

from messaging import Messenger
from vtscan import Vtscan
from writer import Writer
from logger import Logger
from read_conf import Conf
from movies import Movies
from shopping_list import ShoppingList


def send_help_message(channel_id: str):
    """
    Sends the help message in the provided channel id.

    Args:
        channel_id: Id of the channel the help message is ment to be sent.

    Returns:
        None
    """

    help_message = """Commands you can use are :
!help      : For help.
!test      : Test if the bot is available
!scan      : Scans the file for viruses (need file attachment)
!clear     : To clear your shopping list
!add       : To add an item to your shopping list (!add item)
!create    : To create a shopping list for this channel
!see       : To see your shopping list
!remove    : To remove an item from the shopping list
!add_movie : To add a movie to plex (!add_movie Sword Art Online)"""
    messenger.send_message(channel_id, help_message)


def movie_search(search, channel_id: str):
    """
    Searches for a movie and adds it if the user uses the ✅ reaction in discord

    Args:
        search: Name of the movie to search.
        channel_id: Id of the channel to send the response.
        guild_id: Id of the guild (used for replies).
        message_id: Id of the message to reply to.

    Returns:
        None
    """

    keep_trying = True
    i = 0
    while keep_trying:
        i = movies.search_movie(search, i)
        if i == -1:
            keep_trying = False
            break

        title = movies.get_title()
        description = movies.get_description()
        media_id = movies.get_media_id()
        media_type = movies.get_media_type()
        poster = movies.get_poster()

        if not(title and description and media_id and media_type and poster):
            return False

        with open(f"movies/{title}.png", "wb") as file:
            file.write(poster)
            logger.log('debug', "file written sucessfully")

        message = f"Title : {title}\nDescription : {description}"

        embed_params = {
            'title': 'Adding a movie',
            'description': 'Is it this movie ?',
            'color': 13632027,
            'fields': [{'name': 'Title', 'value': title},
                       {'name': 'Description', 'value': description}]
        }

        logger.log('trace', f"Embeds parameters : {embed_params}")

        messenger.send_embed(channel_id, embed_params)
        messenger.send_files(channel_id, [f"movies/{title}.png"])

        message_id = messenger.get_message_id()
        sleep(1)

        messenger.send_reaction(channel_id, message_id, "✅")
        messenger.send_reaction(channel_id, message_id, "❌")

        sleep(1)

        messenger.set_reaction_added(None)

        reaction = messenger.get_reaction_added()
        for i in range(10):
            reaction = messenger.get_reaction_added()
            if reaction:
                break
            sleep(1)
        if reaction == "✅":
            messenger.send_message(channel_id, "Ok adding this movie.")
            message = movies.add_movie(media_type, media_id,
                                       conf['plex_location'])
            messenger.send_message(channel_id, message)
            keep_trying = False
        elif reaction == "❌":
            messenger.send_message(channel_id, "Maybe something else.")
            i += 1
        else:
            keep_trying = False
        messenger.set_reaction_added(None)


def main():
    """
    Main function handles the messages commands and redirects to the desired
    reply function

    Args:
        None

    Returns:
        None
    """

    threads_list = []
    while True:
        message = messenger.get_message()
        if message:
            message = message.lower()
            channel_id = messenger.get_channel_id()
            # author = messenger.get_author_username()
            author_id = messenger.get_author_id()
            message_id = messenger.get_message_id()
            guild_id = messenger.get_guild_id()
            bot_id = "948058941668069386"

            if "<@!" in message:
                pass
            elif message == "!test":
                messenger.send_message(channel_id, "Test sucessful !")

            elif message == "!help":
                send_help_message(channel_id)

            elif message == "!scan":
                attachments = messenger.get_attachments()
                if len(attachments) == 0:
                    messenger.send_message(channel_id,
                                           "Please add a file to scan.",
                                           guild_id, message_id)
                else:
                    messenger.send_message(channel_id, "Scanning ...",
                                           guild_id, message_id)

                    for value in attachments:
                        threads_list.append((ThreadWithResult(
                                             target=scanner.scan,
                                             args=(value["url"], )),
                                             channel_id,
                                             message_id,
                                             guild_id))

                    for thread in threads_list:
                        thread[0].start()

            elif message == "!create":
                shopping_list.create_shopping_list(channel_id)

            elif message == "!clear":
                shopping_list.clear_shopping_list(channel_id)

            elif "!add_movie" in message and author_id != bot_id:
                if message == "!add_movie":
                    messenger.send_message(channel_id,
                                           "No movie name provided")
                else:
                    movie_search(' '.join(message.split(" ")[1:]), channel_id)

            elif "!add" in message and author_id != bot_id:
                add_to_shopping_list(channel_id, message)
            elif message == "!see":
                shopping_list.see_shopping_list(channel_id)
            elif message == "!remove":
                shopping_list.delete_from_shopping_list(channel_id, author_id)
            elif message == "<@!948058941668069386>":
                messenger.send_message(channel_id, "Yes, it's me.")

            else:
                if message and message[0] == "!" and author_id != bot_id:
                    messenger.send_message(channel_id, "Unknown command.")
            messenger.set_message(None)

        thread_list_checker(threads_list)
        sleep(0.3)


def add_to_shopping_list(channel_id, message):
    """
    Adds an tiem to the shopping list

    Args:
        channel_id: Id of the channel to modify the shopping list
        message: message received from discord

    Returns:
        None
    """
    if shopping_list.verify_shopping_list_exists(channel_id):
        if len(message[5:]) < 1:
            messenger.send_message(channel_id, "Usage !add item")
        else:
            shopping_list.add_to_shopping_list(channel_id, message)
    else:
        message = "There is no shopping list" + \
            "created for this channel."
        messenger.send_message(channel_id, message)


def thread_list_checker(threads_list):
    """
    Checks if threads in the list are finished, if so it sends the result in
    the corresponding channel

    Args:
        threads_list: (thread object, channel_id, message_id, guild_id)

    Returns:
        None
    """

    for thread, chan_id, mess_id, gui_id in threads_list:
        if not thread.is_alive():
            thread.join()
            print(f"thread joined {thread.result}")
            threads_list.remove((thread, chan_id, mess_id, gui_id))
            messenger.send_message(chan_id, thread.result, gui_id, mess_id)


def set_status():
    """
    Not implemented yet

    Args:
        None

    Returns:
        None
    """


if __name__ == '__main__':
    logger = Logger('info')
    conf = Conf("config/config.json").load()
    logger.log('special', '\n\n\n\n\n')
    writer = Writer("shopping_list/shopping_list.json")
    messenger = Messenger(conf['Discord_token'], logger)
    messenger.start()
    scanner = Vtscan(conf["Vt_api_key"], logger)
    shopping_list = ShoppingList(messenger, writer)
    movies = Movies(conf['overseerr_endpoint'], conf['PLEX_TOKEN'],
                    logger, messenger)

    main()

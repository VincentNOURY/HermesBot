"""
Shopping list module for discord bot.

Args:
    messenger: An instance of the messenger class.
    writer: An instance of the writer class.
"""

from time import sleep


class ShoppingList:
    """
    Shopping list module for discord bot.

    Args:
        messenger: An instance of the messenger class.
        writer: An instance of the writer class.
    """

    def __init__(self, messenger, writer):
        """
        Initialization of the shopping list module for discord bot.

        Args:
            messenger: An instance of the messenger class.
            writer: An instance of the writer class.
        """

        self.writer = writer
        self.shopping_list = self.writer.load()
        self.messenger = messenger

    def clear_shopping_list(self, channel_id):
        """
        Clears the shopping list (in memory and in the file).

        Args:
            channel_id: Id of the channel to send the response.

        Returns:
            None
        """

        self.shopping_list[channel_id] = []
        self.writer.write(self.shopping_list)
        self.messenger.send_message(channel_id, "Shopping list cleared")

    def add_to_shopping_list(self, channel_id, item):
        """
        Adds an item to the shopping list (in memory and in the file).

        Args:
            item: Object to add to the shopping list.
            channel_id: Id of the channel to send the response.

        Returns:
            None
        """

        item = item[5:].capitalize()
        self.shopping_list[channel_id].append(item)
        self.writer.write(self.shopping_list)
        self.messenger.send_message(channel_id,
                                    f"{item} added to shopping list.")

    def create_shopping_list(self, channel_id):
        """
        Creates an empty shopping list for the specified channel.

        Args:
            channel_id: Id of the channel to send the response,
                        and to add the item to.

        Returns:
            None
        """

        if not self.verify_shopping_list_exists(channel_id):
            self.shopping_list[channel_id] = []
            self.writer.write(self.shopping_list)
            self.messenger.send_message(channel_id, "Shopping list created")
        else:
            message = "A shopping list already exists for this channel!"
            self.messenger.send_message(channel_id, message)

    def verify_shopping_list_exists(self, channel_id):
        """
        Verifies that a shopping list exists for the specified channel.

        Args:
            channel_id: Id of the channel to verify if a shopping list exists.

        Returns:
            Boolean: True if a shopping list exists False otherwise.
        """

        return channel_id in self.shopping_list.keys()

    def see_shopping_list(self, channel_id):
        """
        Displays the content of the shopping list in discord.

        Args:
            channel_id: Id of the channel to send the response
                        and for the shopping list.

        Returns:
            None
        """

        if self.verify_shopping_list_exists(channel_id):
            if self.shopping_list[channel_id] == []:
                self.messenger.send_message(channel_id, "Shopping list empty.")
            else:
                to_send = "Items in the shopping list :"
                for item in self.shopping_list[channel_id]:
                    to_send += f"\n    - {item}"
                self.messenger.send_message(channel_id, to_send)
        else:
            message = "There is no shopping list for this channel !"
            self.messenger.send_message(channel_id, message)

    def delete_from_shopping_list(self, channel_id, author_id):
        """
        Deletes an item from the shopping list.

        Args:
            channel_id: Id of the channel to send the response
                        and for the shopping list.
            author_id: Ensures that only the one that requested the removal
                       of an item can remove it.

        Returns:
            None
        """

        to_send = """Please select a number :"""
        for i in range(len(self.shopping_list[channel_id])):
            to_send += f"\n    {i} : {self.shopping_list[channel_id][i]}"
        to_send += "\nTo cancel just type !cancel"
        self.messenger.send_message(channel_id, to_send)
        message = self.messenger.get_message().lower()
        author = self.messenger.get_author_id().lower()

        while message == to_send.lower() and message != "!cancel":
            sleep(0.2)
            message = self.messenger.get_message().lower()
            author = self.messenger.get_author_id().lower()

        # Would be better with a do-while loop
        while message != "!cancel" and author_id != author:
            message = self.messenger.get_message().lower()
            author = self.messenger.get_author_id().lower()
            sleep(0.2)

        if message != "!cancel":
            if int(message) >= len(self.shopping_list[channel_id]):
                self.messenger.send_message(channel_id, "Index out of range.")
                sleep(0.2)
            else:
                item = self.shopping_list[channel_id].pop(int(message))
                self.writer.write(self.shopping_list)
                self.messenger.send_message(channel_id,
                                            f"{item} has been deleted !")
        else:
            self.messenger.send_message(channel_id, "Sucessfully canceled")

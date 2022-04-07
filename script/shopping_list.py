from time import sleep

class Shopping_list:

    def __init__(self, messenger, writer):
        self.writer = writer
        self.shopping_list = self.writer.load()
        self.messenger = messenger

    def clear_shopping_list(self, channel_id):
        self.shopping_list[channel_id] = []
        self.writer.write(self.shopping_list)
        self.messenger.send_message(channel_id, "Shopping list cleared")

    def add_to_shopping_list(self, channel_id, message):
        item = message[5:].capitalize()
        self.shopping_list[channel_id].append(item)
        self.writer.write(self.shopping_list)
        self.messenger.send_message(channel_id, f"{item} added to shopping list.")

    def create_shopping_list(self, channel_id):
        if not self.verify_shopping_list_exists(channel_id):
            self.shopping_list[channel_id] = []
            self.writer.write(self.shopping_list)
            self.messenger.send_message(channel_id, "Shopping list created")
        else:
            self.messenger.send_message(channel_id, "A shopping list already exists for this channel!")

    def verify_shopping_list_exists(self, channel_id):
        return channel_id in self.shopping_list.keys()

    def see_shopping_list(self, channel_id):
        if self.verify_shopping_list_exists(channel_id):
            if self.shopping_list[channel_id] == []:
                self.messenger.send_message(channel_id, "Shopping list empty.")
            else:
                to_send = "Items in the shopping list :"
                for item in self.shopping_list[channel_id]:
                    to_send += f"\n    - {item}"
                self.messenger.send_message(channel_id, to_send)
        else:
            self.messenger.send_message(channel_id, "There is no shopping list for this channel !")


    def delete_from_shopping_list(self, channel_id, author_id):
        to_send = """Please select a number :"""
        for i in range(len(self.shopping_list[channel_id])):
            to_send += f"\n    {i} : {self.shopping_list[channel_id][i]}"
        to_send += "\nTo cancel just type !cancel"
        self.messenger.send_message(channel_id, to_send)
        message = self.messenger.getMessage().lower()
        author = self.messenger.getAuthorId().lower()

        while message == to_send.lower() and message != "!cancel":
            sleep(0.2)
            message = self.messenger.getMessage().lower()
            author = self.messenger.getAuthorId().lower()

        # Would be better with a do-while loop
        check = True
        while message != "!cancel" and author_id != author:
            message = self.messenger.getMessage().lower()
            author = self.messenger.getAuthorId().lower()
            sleep(0.2)

        if message != "!cancel":
            if int(message) >= len(self.shopping_list[channel_id]):
                self.messenger.send_message(channel_id, "Index out of range.")
                check = False
                sleep(0.2)
            else:
                item = self.shopping_list[channel_id].pop(int(message))
                self.writer.write(self.shopping_list)
                self.messenger.send_message(channel_id, f"{item} has been deleted !")
        else:
            self.messenger.send_message(channel_id, "Sucessfully canceled")

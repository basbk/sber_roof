'''Module, designed to operate with database

Holds set of models, representing same named tables in database and connection settings to db'''

from pony.orm import Required, Optional, Set, Database, PrimaryKey
from telebot.types import ReplyKeyboardMarkup
from config import postgres_config

db = Database()

class MenuItem(db.Entity):
    '''Class, representing one item of menu'''

    title = PrimaryKey(str)
    text = Required(str)
    belongs_to = Required('Menu')
    image_id = Optional(str, unique=True)
    video_id = Optional(str, unique=True)
    forward_to = Optional('Menu', reverse='from_items')

    def send(self, bot, message):
        '''Send a message with all data'''

        if self.image_id is not None and self.image_id is not '':
            bot.send_photo(message.chat.id, self.image_id)
        if self.forward_to is not None and self.forward_to is not '':
            markup = self.forward_to.get_markup()
            bot.send_message(message.chat.id, self.text, reply_markup=markup)
        else:
            bot.send_message(message.chat.id, self.text)
        if self.video_id is not None and self.video_id is not '':
            bot.send_video(message.chat.id, self.video_id)


class Menu(db.Entity):
    '''Class, representing menu itself with method to display it'''

    label = PrimaryKey(str)
    items = Set(MenuItem)
    from_items = Set(MenuItem, reverse='forward_to')

    def get_markup(self):
        '''Create a keyboard to send to user'''

        markup = ReplyKeyboardMarkup(True, False)
        for item in self.items.select():
            markup.add(item.title)
        return markup


class Thesis(db.Entity):
    '''Class, representing thesis, containing info about the text and speaker'''
    text = Required(str)
    speaker = Required(str)


db.bind(**postgres_config)
db.generate_mapping(create_tables=True)

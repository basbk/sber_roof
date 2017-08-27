'''Module, designed to operate with database

Holds set of models, representing same named tables in database and connection settings to db'''

from pony.orm import Required, Optional, Set, Database, PrimaryKey
from telebot.types import ReplyKeyboardMarkup
from config import postgres_config

db = Database()

class MenuItem(db.Entity):
    '''Class, representing one item of menu'''

    title = Required(str)
    text = Required(str)
    belongs_to = Required('Menu')
    image_id = Optional(str, unique=True)
    video_id = Optional(str, unique=True)
    forward_to = Optional('Menu', reverse='from_items')


class Menu(db.Entity):
    '''Class, representing menu itself with method to display it'''

    label = PrimaryKey(str)
    items = Set(MenuItem)
    from_items = Set(MenuItem, reverse='forward_to')

    def get_markup(self):
        '''Create a keyboard to send to user'''

        markup = ReplyKeyboardMarkup(True, False)
        for item in self.items.select().order_by(MenuItem.id):
            markup.add(item.title)
        return markup


class Thesis(db.Entity):
    '''Class, representing thesis, containing info about the text and speaker'''

    text = Required(str)
    speaker = Required(str)


class FlowSubscription(db.Entity):
    '''In this table there are people subscribed for getting thesises'''

    chat_id = PrimaryKey(int)


class Admin(db.Entity):
    '''Table with list of users, who can send thesis'''

    chat_id = PrimaryKey(int)
    in_section = Required(bool)
    choosen_speaker = Optional(str)


class Docs(db.Entity):
    file_id = PrimaryKey(str)


db.bind(**postgres_config)
db.generate_mapping(create_tables=True)

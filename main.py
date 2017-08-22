import os
from flask import Flask, render_template, request
from pony.orm import db_session, desc
from models import Menu, MenuItem, Thesis, FlowSubscription
from config import bot_token
import telebot
import logging


app = Flask(__name__)

bot = telebot.TeleBot(bot_token)
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)


@app.route('/')
def main():
    return render_template('index.html')


@app.route('/update')
@db_session
def update_thesis():
    last_thesis = Thesis.select().order_by(desc(Thesis.id))
    return last_thesis.text


@app.route("/msg", methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@app.route("/msg")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url="https://sber-roof.herokuapp.com/msg")
    return "!", 200


@bot.message_handler(commands=['start'])
@db_session
def handle_start(message):
    '''Handling first interaction with user'''

    bot.send_message(message.chat.id, 'Я знаю все о ВЫШЕ КРЫШ! Что подсказать?🤓', reply_markup=Menu['start'].get_markup())


@bot.message_handler(content_types=['text'])
@db_session
def handle_others(message):
    '''Handle other input from user, displaying different menus'''

    m_item = MenuItem.select(lambda m: m.title == message.text).first()
    if m_item != None:
        reply(m_item, message)
    


def reply(item, message):
        '''Send a message with all data'''
        if item.belongs_to == Menu['flow']:
                FlowSubscription[message.chat.id].delete()
        if item.image_id is not None and item.image_id is not '':
            bot.send_photo(message.chat.id, item.image_id)
        if item.forward_to is not None and item.forward_to is not '':
            markup = item.forward_to.get_markup()
            bot.send_message(message.chat.id, item.text, reply_markup=markup)
            if item.forward_to == Menu['flow']:
                FlowSubscription(chat_id=message.chat.id)
        else:
            bot.send_message(message.chat.id, item.text)
        if item.video_id is not None and item.video_id is not '':
            bot.send_video(message.chat.id, item.video_id)


if __name__ == '__main__':
    app.run(threaded=True, host="0.0.0.0", port=os.environ.get('PORT', 5000))
    
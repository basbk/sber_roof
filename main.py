import os
from flask import Flask, render_template, request
from pony.orm import db_session, desc
from models import Menu, MenuItem, Thesis
from config import bot_token
import telebot
import logging


app = Flask(__name__)

bot = telebot.TeleBot(bot_token)
#logger = telebot.logger
#telebot.logger.setLevel(logging.DEBUG)


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

    bot.send_message(message.chat.id, 'Я знаю все о SBERROOF! Что подсказать?🤓', reply_markup=Menu['start'].get_markup())


@bot.message_handler(content_types=['text'])
@db_session
def handle_others(message):
    '''Handle other input from user, displaying different menus'''

    m_item = MenuItem.get(title=message.text)
    if m_item != None:
        m_item.send(bot, message)


if __name__ == '__main__':
    app.run(threaded=True, host="0.0.0.0", port=os.environ.get('PORT', 5000))
    
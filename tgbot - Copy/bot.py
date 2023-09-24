import os

import telebot


bot = telebot.TeleBot('6380916143:AAFRTgU0SV-UHzFNidxMzQrlozbTNRr_s7k')

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, message.text)

bot.infinity_polling()
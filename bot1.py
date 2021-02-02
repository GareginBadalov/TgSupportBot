import importlib

import telebot
from bs4 import BeautifulSoup
from telebot import types
import urllib.request
from urllib.parse import quote
import re
import config
import requests

bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    mu_button1 = types.KeyboardButton("☁ Погода")
    mu_button2 = types.KeyboardButton("💲Курсы валют")
    mu_button3 = types.KeyboardButton("ᐈ Видео на Youtube")
    mu_button4 = types.KeyboardButton("🔎 Запрос википедии")
    name = bot.get_me().first_name
    markup.add(mu_button1, mu_button2, mu_button3, mu_button4)
    bot.send_message(message.chat.id, f'{message.from_user.first_name}, Welcome to the {name}', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "☁ Погода")
def choise(message):
    markup = types.ReplyKeyboardRemove(selective=False)
    bot.send_message(message.chat.id, 'Введите"/погода", а затем название городачерез пробел. Пример:/погода Москва',
                     reply_markup=markup)


@bot.message_handler(func=lambda message: '/погода' in message.text)
def weather(message):
    try:
        city = message.text[8:]
        observation = config.mgr.weather_at_place(city)
        w = observation.weather

        temp = w.temperature('celsius')['temp']
        bot.send_message(message.chat.id, f'В городе {city}, сейчас {str(temp)} градусов')
    except Exception:
        bot.send_message(message.chat.id, f'Название города неккоректно попробуйте еще раз')


@bot.message_handler(func=lambda message: message.text == "💲Курсы валют")
def choise1(message):
    markup_in = types.InlineKeyboardMarkup(row_width=3)
    mu_in_button1 = types.InlineKeyboardButton('Доллар', callback_data='dlr')
    mu_in_button2 = types.InlineKeyboardButton('Евро', callback_data='eur')
    mu_in_button3 = types.InlineKeyboardButton('Гривна', callback_data='grvn')
    markup_in.add(mu_in_button1, mu_in_button2, mu_in_button3)
    bot.send_message(message.chat.id, 'Введите валюту из списка', reply_markup=markup_in)


@bot.message_handler(func=lambda message: message.text == "ᐈ Видео на Youtube")
def choise2(message):
    markup_in2 = types.InlineKeyboardMarkup(row_width=1)
    mu2_in_button1 = types.InlineKeyboardButton('Искать', callback_data='go')
    markup_in2.add(mu2_in_button1)
    bot.send_message(message.chat.id,
                     'Помните, что данная функция выводит только первое видео. Нажмите искать и введите запрос: ',
                     reply_markup=markup_in2)


@bot.message_handler(func=lambda message: message.text == "🔎 Запрос википедии")
def choise3(message):
    bot.send_message(message.chat.id,
                     'Введите свой запрос прямо в текст сообщения, только напишите перед ним "@wiki". Например: @wiki Моцарт')


@bot.callback_query_handler(func=lambda call: True)
def courses(call):
    try:
        if call.message:
            if call.data == 'grvn':
                full_page = requests.get(config.grvn_rub, headers=config.header)
                soup = BeautifulSoup(full_page.content, 'html.parser')
                convert = soup.findAll('span', {'class': 'DFlfde', 'class': 'SwHCTb', 'data-precision': 2})
                bot.send_message(call.message.chat.id, f'На данный момент гривна стоит {convert[0].text} руб.')
            elif call.data == 'dlr':
                full_page1 = requests.get(config.dollar_rub, headers=config.header)
                soup1 = BeautifulSoup(full_page1.content, 'html.parser')
                convert1 = soup1.findAll('span', {'class': 'DFlfde', 'class': 'SwHCTb', 'data-precision': 2})
                bot.send_message(call.message.chat.id, f'На данный момент доллар стоит {convert1[0].text} руб.')
            elif call.data == 'eur':
                full_page2 = requests.get(config.euro_rub, headers=config.header)
                soup2 = BeautifulSoup(full_page2.content, 'html.parser')
                convert2 = soup2.findAll('span', {'class': 'DFlfde', 'class': 'SwHCTb', 'data-precision': 2})
                bot.send_message(call.message.chat.id, f'На данный момент евро стоит {convert2[0].text} руб.')
            elif call.data == 'go':
                @bot.message_handler(content_types=['text'])
                def search(message):

                    html = urllib.request.urlopen(f'https://www.youtube.com/results?search_query={quote(message.text)}')
                    video_ids = re.findall(r'watch\?v=(\S{11})', html.read().decode())
                    a = 'https://www.youtube.com/watch?v=' + video_ids[0]
                    bot.send_message(message.chat.id, a)




    except:
        pass


bot.polling(none_stop=True)

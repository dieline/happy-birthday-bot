from telebot.types import KeyboardButton, ReplyKeyboardMarkup
from telebot.async_telebot import AsyncTeleBot
import asyncio

MONTHES = {'Январь': 31, 'Февраль': 29, 'Март': 31, 'Апрель': 30,
           'Май': 31, 'Июнь': 30, 'Июль': 31, 'Август': 31,
           'Сентярь': 30, 'Октябрь': 31, 'Ноябрь': 30, 'Декабрь': 31}
TOKEN = '6801000433:AAFxb9rCFs8dtZukC_Peu9ZgIYlGuew4gG0'
bot = AsyncTeleBot(TOKEN)


@bot.message_handler(commands=['start'])
async def start(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton('Записать дату рождения'))
    await bot.reply_to(message, '''Напомню участникам групп, в которых вы состоите,
                                    о вашем дне рождения за неделю и день до его начала,
                                    а в сам день поздравлю вас!''', reply_markup=markup)


@bot.message_handler(commands=['help'])
async def start(message):
    await bot.reply_to(message, '''Напомню участникам групп, в которых вы состоите,
                                о вашем дне рождения за неделю и день до его начала,
                                а в сам день поздравлю вас!''')


@bot.message_handler(content_types=['text'])
async def keyboard_handler(message):
    if message.text == 'Записать дату рождения' or message.text == 'Изменить дату рождения':
        month_markup = ReplyKeyboardMarkup(resize_keyboard=True)
        month_markup.add(*MONTHES.keys())
        await bot.reply_to(message, 'Месяц рождения?', reply_markup=month_markup)
    if message.text in MONTHES.keys():
        month = message.text  # Сохранить в БД
        days_markup = ReplyKeyboardMarkup(resize_keyboard=True)
        days_markup.add(*list(map(str, range(1, MONTHES[message.text] + 1))))
        await bot.reply_to(message, 'День рождения?', reply_markup=days_markup)
    if message.text.isnumeric():  # Проверка на валидность введенного дня будет... потом
        day = int(message.text)  # Сохранить в БД
        markup = ReplyKeyboardMarkup(resize_keyboard=True).add(
            KeyboardButton('Записать дату рождения'), KeyboardButton('Изменить дату рождения'))
        await bot.reply_to(message, 'День рождения записан!', reply_markup=markup)


asyncio.run(bot.polling())

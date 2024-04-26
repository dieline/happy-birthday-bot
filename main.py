import telebot
from telebot import types
bot = telebot.TeleBot('6801000433:AAFxb9rCFs8dtZukC_Peu9ZgIYlGuew4gG0')


@bot.message_handler(commands = ['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
    item1 = types.KeyboardButton('поздравит с днем рождения')
    markup.add(item1)
    bot.send_message(message.chat.id, f'привет, {message.from_user.first_name}', reply_markup = markup)

@bot.message_handler(content_types= ['text'])
def bot_message(message):
    if message.text == 'поздравит с днем рождения':
        bot.send_message(message.chat.id, 'Когда(месяц)?')


bot.polling(none_stop = True)
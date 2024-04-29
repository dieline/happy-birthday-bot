from telebot.types import KeyboardButton, ReplyKeyboardMarkup, Chat, Message
from telebot.async_telebot import AsyncTeleBot
import asyncio
import sqlite3
from datetime import date, timedelta

BEFORE_WEEK = timedelta(days=7)
BEFORE_DAY = timedelta(days=1)
MONTHES = {'Январь': 31, 'Февраль': 29, 'Март': 31, 'Апрель': 30,
           'Май': 31, 'Июнь': 30, 'Июль': 31, 'Август': 31,
           'Сентярь': 30, 'Октябрь': 31, 'Ноябрь': 30, 'Декабрь': 31}
MONTHES_ENUM = {'Январь': 1, 'Февраль': 2, 'Март': 3, 'Апрель': 4,
                'Май': 5, 'Июнь': 6, 'Июль': 7, 'Август': 8,
                'Сентярь': 9, 'Октябрь': 10, 'Ноябрь': 11, 'Декабрь': 12}
TOKEN = '6801000433:AAFxb9rCFs8dtZukC_Peu9ZgIYlGuew4gG0'
bot = AsyncTeleBot(TOKEN)
connect = sqlite3.connect('users_database.sqlite')
cursor = connect.cursor()
chats = cursor.execute('SELECT chat_id FROM birthdays').fetchall()


async def congratulate(chat_id):
    birthday = date.today()
    day_before_birthday = date.today() + BEFORE_DAY
    week_before_birthday = date.today() + BEFORE_WEEK
    for user in cursor.execute('SELECT * FROM birthdays WHERE bday_day = ? AND bday_month = ? AND chat_id = ?',
                               (birthday.day, birthday.month, chat_id)).fetchall():
        await bot.send_message(chat_id, f"Сегодня у {user[4]} день рождения!")
    for user in cursor.execute('SELECT * FROM birthdays WHERE bday_day = ? AND bday_month = ? AND chat_id = ?',
                               (day_before_birthday.day, day_before_birthday.month, chat_id)).fetchall():
        await bot.send_message(chat_id, f"Завтра у {user[4]} день рождения!")
    for user in cursor.execute('SELECT * FROM birthdays WHERE bday_day = ? AND bday_month = ? AND chat_id = ?',
                               (week_before_birthday.day, week_before_birthday.month, chat_id)).fetchall():
        await bot.send_message(chat_id, f"Через неделю у {user[4]} день рождения!")


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
async def text_handler(message: Message):
    if message.chat.type == "private":
        if message.text == 'Записать дату рождения' or message.text == 'Изменить дату рождения':
            month_markup = ReplyKeyboardMarkup(resize_keyboard=True)
            month_markup.add(*MONTHES.keys())
            await bot.reply_to(message, 'Месяц рождения?', reply_markup=month_markup)
        if message.text in MONTHES.keys():
            month = MONTHES_ENUM[message.text]
            user_id = int(message.from_user.id)
            first_name = message.from_user.first_name
            if len(cursor.execute('SELECT * FROM birthdays WHERE user_id = ?', (user_id,)).fetchall()) == 0:
                cursor.execute('INSERT INTO birthdays(first_name, user_id, bday_month) VALUES(?, ?, ?)',
                               (first_name, user_id, month))
            else:
                cursor.execute('UPDATE birthdays SET first_name = ?, bday_month = ? WHERE user_id = ?',
                               (first_name, month, user_id))
                connect.commit()
            days_markup = ReplyKeyboardMarkup(resize_keyboard=True)
            days_markup.add(*list(map(str, range(1, MONTHES[message.text] + 1))))
            await bot.reply_to(message, 'День рождения?', reply_markup=days_markup)
        if message.text.isnumeric():  # Проверка на валидность введенного дня будет... потом
            day = int(message.text)
            user_id = int(message.from_user.id)
            first_name = message.from_user.first_name
            if cursor.execute('SELECT * FROM birthdays WHERE user_id = ?', (user_id,)).fetchall() == 0:
                cursor.execute('INSERT INTO birthdays(first_name, user_id, bday_day) VALUES(?, ?)',
                               (first_name, user_id, day))
                connect.commit()
            else:
                cursor.execute('UPDATE birthdays SET first_name = ?, bday_day = ? WHERE user_id = ?',
                               (first_name, day, user_id))
                connect.commit()
            connect.commit()
            markup = ReplyKeyboardMarkup(resize_keyboard=True).add(
                KeyboardButton('Записать дату рождения'), KeyboardButton('Изменить дату рождения'))
            await bot.reply_to(message, 'День рождения записан!', reply_markup=markup)
    else:
        chat_id = int(message.chat.id)
        first_name = message.from_user.first_name
        user_id = int(message.from_user.id)  # У API нет метода получения участников, поэтому вытягиваем id из сообщений
        if len(cursor.execute('SELECT * FROM birthdays WHERE user_id = ?',
                              (user_id,)).fetchall()) == 0:
            cursor.execute('INSERT INTO birthdays(first_name, chat_id, user_id) VALUES(?, ?, ?)',
                           (first_name, chat_id, user_id))
            connect.commit()
        else:
            cursor.execute('UPDATE birthdays SET first_name = ?, chat_id = ? WHERE user_id = ?',
                           (first_name, chat_id, user_id))
            connect.commit()


def main():
    asyncio.run(bot.polling())


if __name__ == "__main__":
    main()

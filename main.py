from typing import Union
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter, BaseFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import asyncio
import sqlite3
from datetime import date
from constants import *
from get_chat_members import get_chat_members
from apscheduler.schedulers.asyncio import AsyncIOScheduler

bot = Bot(TOKEN)
dp = Dispatcher(storage=MemoryStorage())

connect = sqlite3.connect('users_database.sqlite')
cursor = connect.cursor()
chats = cursor.execute('SELECT chat_id FROM birthdays').fetchall()


class ChatFilter(BaseFilter):
    def __init__(self, chat_type: Union[str, list]):
        self.chat_type = chat_type

    async def __call__(self, message: types.Message) -> bool:
        if isinstance(self.chat_type, str):
            return self.chat_type == message.chat.type
        else:
            return message.chat.type in self.chat_type


class TextFilter(BaseFilter):
    def __init__(self, message_text: Union[str, list]):
        self.message_text = message_text

    async def __call__(self, message: types.Message) -> bool:
        if isinstance(self.message_text, str):
            return self.message_text.lower() == message.text.lower()
        else:
            return message.text.lower() in self.message_text


class WriteStates(StatesGroup):
    choosing_month = State()
    choosing_day = State()


def make_keyboard(col_num, iterator):
    keyboard = ReplyKeyboardBuilder()
    for elem in iterator:
        keyboard.add(types.KeyboardButton(text=str(elem)))
    keyboard.adjust(col_num)
    return keyboard


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


@dp.message(Command('start'))
async def start(message: types.Message):
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(types.KeyboardButton(text="Записать дату рождения"))
    await message.reply('''Напомню участникам групп, в которых вы состоите,
                           о вашем дне рождения за неделю и день до его начала,
                           а в сам день поздравлю вас!''',
                        reply_markup=keyboard.as_markup(resize_keyboard=True))
    print(start.__name__)


@dp.message(Command('help'))
async def help_command(message):
    await message.reply('''Напомню участникам групп, в которых вы состоите,
                           о вашем дне рождения за неделю и день до его начала,
                           а в сам день поздравлю вас!''')
    print(help_command.__name__)


@dp.message(StateFilter(None),
            TextFilter(message_text=["записать дату рождения", "изменить дату рождения"]),
            ChatFilter(chat_type="private"))
async def write_start(message: types.Message, state: FSMContext):
    keyboard = make_keyboard(3, MONTHES.keys())
    await message.reply('Месяц рождения?', reply_markup=keyboard.as_markup(resize_keyboard=True))
    await state.set_state(WriteStates.choosing_month)
    print(write_start.__name__)


@dp.message(WriteStates.choosing_month,
            F.text.in_(MONTHES.keys()),
            ChatFilter(chat_type="private"))
async def choose_month(message: types.Message, state: FSMContext):
    await state.update_data(bday_month=MONTHES_ENUM[message.text.lower()])
    keyboard = make_keyboard(6, range(1, MONTHES[message.text] + 1))
    await message.reply('День рождения?', reply_markup=keyboard.as_markup(resize_keyboard=True))
    await state.set_state(WriteStates.choosing_day)
    print(choose_month.__name__)


@dp.message(WriteStates.choosing_month,
            ChatFilter(chat_type="private"))
async def choose_month_incorrect(message: types.Message):
    keyboard = make_keyboard(3, MONTHES.keys())
    await message.answer("Неверно введен месяц, попробуйте снова.",
                         reply_markup=keyboard.as_markup(resize_keyboard=True))


@dp.message(WriteStates.choosing_day,
            F.text.in_(list(map(str, list(range(1, 32))))),
            ChatFilter(chat_type="private"))  # Если пользователь выберет 30 февраля - приду и прибью его
async def choose_day(message: types.Message, state: FSMContext):
    birthday = await state.get_data()
    await message.reply("День рождения записан!",
                        reply_markup=types.reply_keyboard_remove.ReplyKeyboardRemove())
    bday_month = int(birthday["bday_month"])
    bday_day = int(message.text)
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    if len(cursor.execute('SELECT * FROM birthdays WHERE user_id = ?', (user_id,)).fetchall()) == 0:
        cursor.execute('INSERT INTO birthdays(first_name, user_id, bday_month, bday_day) VALUES(?, ?, ?, ?)',
                       (first_name, user_id, bday_month, bday_day))
    else:
        cursor.execute('UPDATE birthdays SET first_name = ?, bday_month = ?, bday_day = ? WHERE user_id = ?',
                       (first_name, bday_month, bday_day, user_id))
    connect.commit()
    await state.clear()
    print(choose_day.__name__)


@dp.message(WriteStates.choosing_day,
            ChatFilter(chat_type="private"))
async def choose_day_incorrect(message: types.Message, state: FSMContext):
    await message.reply("Неверно введен месяц, попробуйте снова.")


@dp.message(F.content_type.in_({'new_chat_members'}),
            ChatFilter(chat_type="group"))
async def write_chat_members(message: types.Message):
    chat_members = await get_chat_members(chat_id=message.chat.id)
    for member in chat_members:
        member_id = member.user.id
        first_name = member.user.first_name
        if len(cursor.execute('SELECT * FROM birthdays WHERE user_id = ?',
                              (member_id,)).fetchall()) == 0:
            cursor.execute('INSERT INTO birthdays(first_name, chat_id, user_id) VALUES(?, ?, ?)',
                           (first_name, message.chat.id, member_id))
        else:
            cursor.execute('UPDATE birthdays SET first_name = ?, chat_id = ? WHERE user_id = ?',
                           (first_name, message.chat.id, member_id))
        connect.commit()


async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(congratulate, 'interval', days=1)
    scheduler.start()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

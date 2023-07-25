from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from pyowm import OWM
from pyowm.utils import config
from pyowm.utils import timestamps
from pyowm.utils.config import get_default_config
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import ChatType
import sqlite3
from aiogram import *
import time
import random
from aiogram import Bot, Dispatcher, types
import sqlite3
# Initialize a list to store the already printed lines
printed_lines = []
# Connect to the SQLite database
conn = sqlite3.connect('marketdb')
cursor = conn.cursor()
last_line_index = 0
# Connect to the database
cursor.execute("PRAGMA foreign_keys = 0;")

cursor.execute("CREATE TABLE sqlitestudio_temp_table AS SELECT * FROM places;")

cursor.execute("DROP TABLE places;")

cursor.execute("CREATE TABLE places (placename TEXT, placeowner TEXT, placething TEXT, placedescription TEXT, placeraiting INTEGER, placereports INTEGER, placeclass TEXT);")

cursor.execute("INSERT INTO places (placename, placeowner, placething, placedescription, placeraiting, placereports, placeclass) SELECT placename, placeowner, placething, placedescription, placeraiting, placereports, placeclass FROM sqlitestudio_temp_table;")

cursor.execute("DROP TABLE sqlitestudio_temp_table;")

cursor.execute("PRAGMA foreign_keys = 1;")

# Commit the changes to the database
conn.commit()


class MyBot:
    #инициализация бота
    def __init__(self):
        self._TOKEN = '6566069092:AAFABgofnFkx_tT0GQvTik06ZvTnD_yCsH8'#токен
        self.bot = Bot(self._TOKEN)
        self.dp = Dispatcher(bot=self.bot, storage=MemoryStorage())
        self.memory = MemoryStorage()



    def start(self):
        inline_btn_1 = InlineKeyboardButton('report', callback_data='report')
        inline_btn_2 = InlineKeyboardButton('rep-', callback_data='repdw')
        inline_btn_3 = InlineKeyboardButton('rep+', callback_data='repup')
        inline_kb1 = InlineKeyboardMarkup().add(inline_btn_1, inline_btn_2, inline_btn_3)
        help_button = KeyboardButton('/help')
        price_button = KeyboardButton('/checkplaces')
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(help_button, price_button)

        @self.dp.message_handler(commands=['help'])
        async def hello(message: types.message):
            await message.answer('что умеет этот бот???\n/checkplaces - начать смотреть карточки и показать следующую.', reply_markup=keyboard)
    
        @self.dp.callback_query_handler(lambda c: c.data == 'report')
        async def process_callback_button1(callback_query: types.CallbackQuery):
            cursor.execute("UPDATE places SET placereports = placereports + 1")
            conn.commit()
            await callback_query.answer()
            await callback_query.message.answer('Репорт отправлен')

        @self.dp.callback_query_handler(lambda c: c.data == 'repup')
        async def process_callback_button2(callback_query: types.CallbackQuery):
            cursor.execute("UPDATE places SET placeraiting = placeraiting + 1")
            conn.commit()
            await callback_query.answer()
            await callback_query.message.answer('Репутация карточки повышена')

        @self.dp.callback_query_handler(lambda c: c.data == 'repdw')
        async def process_callback_button3(callback_query: types.CallbackQuery):
            cursor.execute("UPDATE places SET placeraiting = placeraiting - 1")
            conn.commit()
            await callback_query.answer()
            await callback_query.message.answer('Репутация карточки понижена')


        @self.dp.message_handler(commands=['checkplaces'])
        async def get_random_line(message: types.Message):
            global last_line_index

            cursor.execute("SELECT placename, placeowner, placething, placedescription, placeraiting, placeclass FROM places")
            all_lines = cursor.fetchall()

            available_lines = [line for line in all_lines if line[0] not in printed_lines]

            if available_lines:
                if last_line_index >= len(available_lines):
                    last_line_index = 0

                next_line = available_lines[last_line_index]

                line_message = f"Place Name: {next_line[0]}\nPlace Owner: {next_line[1]}\nPlace Thing: {next_line[2]}\nPlace Description: {next_line[3]}\nPlace Rating: {next_line[4]}\nPlace Class: {next_line[5]}"

                await message.answer(line_message, reply_markup=inline_kb1)

                last_line_index += 1
            else:
                await message.answer("No more lines available.")




#запуск сервера
        executor.start_polling(self.dp, skip_updates=True)
#старт сервера
if __name__ == '__main__':
    bot = MyBot()
    bot.start()
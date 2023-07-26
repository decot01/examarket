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
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.types.reply_keyboard import ReplyKeyboardRemove
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from aiogram import types
import sqlite3
import time 

# Connect to the database
conn = sqlite3.connect('marketdb')
cursor = conn.cursor()
printed_lines = []
last_line_index = 0
# Execute the SQL statements
cursor.execute("PRAGMA foreign_keys = 0;")

cursor.execute("CREATE TABLE sqlitestudio_temp_table AS SELECT * FROM places;")

cursor.execute("DROP TABLE places;")

cursor.execute("CREATE TABLE places (placename TEXT, placeowner TEXT, placething TEXT, placedescription TEXT, placeraiting INTEGER, placereports INTEGER, placeclass TEXT);")

cursor.execute("INSERT INTO places (placename, placeowner, placething, placedescription, placeraiting, placereports, placeclass) SELECT placename, placeowner, placething, placedescription, placeraiting, placereports, placeclass FROM sqlitestudio_temp_table;")

cursor.execute("DROP TABLE sqlitestudio_temp_table;")

cursor.execute("PRAGMA foreign_keys = 1;")

# Commit the changes to the database
conn.commit()

# Close the connection
conn.close()


#класс
class MyBot(FSMContext,StatesGroup): 
    # Создаем именованные состояния (states) для каждой стадии опроса
    PLACE_NAME = State()
    PLACE_OWNER = State()
    PLACE_THING = State()
    PLACE_DESCRIPTION = State()
    PLACE_CLASS = State()

    #инициализация бота
    def __init__(self):
        self._TOKEN = '6566069092:AAFABgofnFkx_tT0GQvTik06ZvTnD_yCsH8'#токен
        self.bot = Bot(self._TOKEN)
        self.dp = Dispatcher(bot=self.bot, storage=MemoryStorage())
        self.memory = MemoryStorage()

    def start(self):
        #элементы клавиатуры (не к регистрации) не инлайн
        help_button = KeyboardButton('/help')
        faq_button = KeyboardButton('/faq')
        info_button = KeyboardButton('/info')
        add_button = KeyboardButton('/addplace')
        price_button = KeyboardButton('/checkplaces')        
        main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        main_keyboard.add(help_button,info_button, add_button, price_button, faq_button)
        inline_btn_1 = InlineKeyboardButton('report', callback_data='report')
        inline_btn_2 = InlineKeyboardButton('rep-', callback_data='repdw')
        inline_btn_3 = InlineKeyboardButton('rep+', callback_data='repup')
        inline_kb1 = InlineKeyboardMarkup().add(inline_btn_1, inline_btn_2, inline_btn_3)


        #команды
        @self.dp.message_handler(commands=['start'])
        async def hello(message: types.message):
            await message.answer('привет напиши /help что бы узнать список команд.')
        @self.dp.message_handler(commands=['faq'])
        async def hello(message: types.message):
            await message.answer('привет напиши /help что бы узнать список команд.')

        @self.dp.message_handler(commands=['menu'])
        async def hello(message: types.message):
            await message.answer('снизу показанно меню.', reply_markup=main_keyboard)

        @self.dp.message_handler(commands=['help'])
        async def hello(message: types.message):
            await message.answer('что умеет этот бот???\n/info - о нас.\n/reg - зарегестрироваться на площадке\n/addplace - добавить товар на площадку\nесли вы нашли ошибку просто очистите чат с ботом и все!', reply_markup=main_keyboard)
    
        @self.dp.message_handler(commands=['info'])
        async def hello(message: types.message):
            await message.answer('мы первый марркетплейс на экзархии в обход магазину', reply_markup=main_keyboard)


        @self.dp.message_handler(commands=['help'])
        async def hello(message: types.message):
            await message.answer('что умеет этот бот???\n/checkplaces - начать смотреть карточки и показать следующую.', reply_markup=main_keyboard)
    
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

    def addplace(self):
        menu_button = KeyboardButton('/menu')
        keyboard_menu = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        keyboard_menu.add(menu_button)
        storred = InlineKeyboardButton('купленно в магазине', callback_data='storred')
        unstorred = InlineKeyboardButton('не купленно в магазине', callback_data='unstorred')
        storredkb = InlineKeyboardMarkup().add(storred, unstorred )

        @self.dp.callback_query_handler(text='storred')
        async def send_message(callback_query: types.CallbackQuery):
        # Отправляем сообщение от пользователя
            await callback_query.message.answer('купленно в магазине')
        @self.dp.callback_query_handler(text='unstorred')
        async def send_message(callback_query: types.CallbackQuery):
        # Отправляем сообщение от пользователя
            await callback_query.message.answer('не купленно в магазине')
        # Обработчик команды "/addplace"
        @self.dp.message_handler(Command('addplace'))
        async def start_addplace(message: types.Message):
            await MyBot.PLACE_NAME.set()
            await message.answer('Введите название карточки:')
    
        @self.dp.message_handler(state=MyBot.PLACE_NAME)
        async def process_name(message: types.Message, state: FSMContext):
            async with state.proxy() as data:
                data['placename'] = message.text
            await MyBot.PLACE_THING.set()
            await message.answer('Введите что вы продаете (1 товар):')

        @self.dp.message_handler(state=MyBot.PLACE_THING)
        async def process_thing(message: Message, state: FSMContext):
            async with state.proxy() as data:
                data['placething'] = message.text
            await MyBot.PLACE_DESCRIPTION.set()
            await message.answer('Введите описание товара')

        @self.dp.message_handler(state=MyBot.PLACE_DESCRIPTION)
        async def process_description(message: Message, state: FSMContext):
            async with state.proxy() as data:
                data['placedescription'] = message.text
            await MyBot.PLACE_CLASS.set()
            await message.answer('Введите класс товара (купленное в магазине или нет)',reply_markup=storredkb)

        @self.dp.message_handler(state=MyBot.PLACE_CLASS)
        async def process_class(message: Message, state: FSMContext):
            async with state.proxy() as data:
                data['placeclass'] = message.text
            await MyBot.PLACE_OWNER.set()
            await message.answer('Введите ник на экзархии и в тг')

        @self.dp.message_handler(state=MyBot.PLACE_OWNER)
        async def process_owner(message: Message, state: FSMContext):
            async with state.proxy() as data:
                data['placeowner'] = message.text

            async with state.proxy() as data:
                placename = data['placename']
                placething = data['placething']
                placedescription = data['placedescription']
                placeclass = data['placeclass']
                placeowner = data['placeowner']

                # Open the database connection
                conn = sqlite3.connect('marketdb')

                # Insert the data into the database
                conn.execute("INSERT INTO places (placename, placething, placedescription, placeclass, placeowner) VALUES (?, ?, ?, ?, ?)",
                            (placename, placething, placedescription, placeclass, placeowner))
                conn.commit()

                # Close the database connection
                conn.close()

                await message.answer(f"Ваша анкета успешно принята!\nВот ваши данные:\nназвание карточки: {placename}\nобъект продажи: {placething}\nописание: {placedescription}\класс: {placeclass}\nЧтобы выйти из заполнения анкеты пропишите любой символ, например ! и отправьте команду /menu", reply_markup=keyboard_menu)
                print("человек завершил выставление товара! Время:", time.ctime())

            await state.finish()

        # Запуск сервера
        executor.start_polling(self.dp, skip_updates=True)


if __name__ == '__main__':
    bot = MyBot()
    bot.start()
    bot.addplace()
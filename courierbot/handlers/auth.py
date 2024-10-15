from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery

from pathlib import Path

import re
import os
import hashlib
from courierbot.db import BotDBClass
import courierbot.kb

from decimal import Decimal

BotDB=BotDBClass(Path(__file__).resolve().parent.parent.parent/'db.sqlite3')

class OrderAuth(StatesGroup):
    waiting_for_username=State()
    waiting_for_password=State()



# Обратите внимание: есть второй аргумент
async def auth_start(clbck: CallbackQuery, state: FSMContext):
    await clbck.message.answer("Введите ник на сайте:")
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    await state.set_state(OrderAuth.waiting_for_username.state)


async def auth_username(message: types.Message, state: FSMContext):
    await state.update_data(username=message.text)

    await state.set_state(OrderAuth.waiting_for_password.state)
    await message.bot.send_message(message.chat.id, "Введите пароль:")

async def auth(message: types.Message, state: FSMContext):
    await state.update_data(password=message.text)
    user_data = await state.get_data()

    if BotDB.check_user(user_data['username'],user_data['password']):

        if not BotDB.user_profile_exists(BotDB.check_user(user_data['username'],user_data['password'])):
            # salt = os.urandom(32)
            # key = hashlib.pbkdf2_hmac('sha256', message.text.encode('utf-8'), salt, 100000)
            # await state.update_data(salt=salt)
            #await state.update_data(password=key)
            BotDB.add_user_profile(user_data['username'], BotDB.check_user(user_data['username'], user_data['password']),
                                   'seller', message.chat.id, user_data['password'])#,salt)
        else:
            # salt = os.urandom(32)
            # key = hashlib.pbkdf2_hmac('sha256', message.text.encode('utf-8'), salt, 100000)
            # await state.update_data(salt=salt)

            BotDB.reg_bot(message.chat.id,message.text,BotDB.get_user_id_by_username(user_data['username']))#hashlib.pbkdf2_hmac('sha256', message.text.encode('utf-8'), salt, 100000),user_data['salt'])
        await message.bot.send_message(message.from_user.id,
                                       f"Добро пожаловать, {message.from_user.first_name}. Выберите действие в меню",
                                       reply_markup=courierbot.kb.menu)

def register_handlers_auth(dp: Dispatcher):
    dp.register_callback_query_handler(auth_start, lambda callback_query: callback_query.data == "auth",state="*")
    #dp.register_message_handler(earned_start, commands="earned", state="*")
    dp.register_message_handler(auth_username, state=OrderAuth.waiting_for_username)
    dp.register_message_handler(auth, state=OrderAuth.waiting_for_password)
    #dp.register_message_handler(earned_sum_chosen, state=OrderEarned.waiting_for_earned_sum)

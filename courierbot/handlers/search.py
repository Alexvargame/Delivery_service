from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery
import re
from db import BotDBClass
from decimal import Decimal
BotDB=BotDBClass('db.db')
import kb
class OrderSearch(StatesGroup):
    waiting_for_search = State()


# Обратите внимание: есть второй аргумент
async def search_start(clbck: CallbackQuery, state: FSMContext):
    await clbck.message.answer("Что ищем?:")
    await state.set_state(OrderSearch.waiting_for_search.state)

async def search(message: types.Message, state: FSMContext):
    await state.update_data(search=message.text.capitalize())
    search_result=BotDB.get_search(message.chat.id,message.text.capitalize(),'s')

    search_result.extend(BotDB.get_search(message.chat.id,message.text.capitalize(),'e'))
    if len(search_result)>0:
        for s in search_result:
                await message.answer(f"Статья: {s[3]}\n Cумма:  {s[4]}\n Дата: {s[5].split()[0]}")
        await message.bot.send_message(message.from_user.id,
                                       f"Добро пожаловать. Выберите действие в меню",
                                       reply_markup=kb.menu)

    else:
        await message.answer("Вы не указали условия поиска")






def register_handlers_search(dp: Dispatcher):
    dp.register_callback_query_handler(search_start, lambda callback_query: callback_query.data == "search",state="*")
    #dp.register_message_handler(search_start, commands="search", state="*")
    dp.register_message_handler(search, state=OrderSearch.waiting_for_search)

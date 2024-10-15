from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery
import re
from courierbot.db import BotDBClass
import courierbot.kb
from decimal import Decimal

from pathlib import Path

BotDB=BotDBClass(Path(__file__).resolve().parent.parent.parent/'db.sqlite3')



class OrderBalance(StatesGroup):
    waiting_for_balance = State()



async def balance_start(clbck: CallbackQuery,state: FSMContext):
    user_balance = BotDB.get_user_balance(clbck.message.chat.id)
    await clbck.message.answer(f"Ваш балансе:"'{0:.2f}'.format(BotDB.get_user_balance(clbck.message.chat.id)))
    await clbck.message.bot.send_message(clbck.message.chat.id,f"Выберите действие в меню",reply_markup=courierbot.kb.menu)
    await state.finish()



def register_handlers_balance(dp: Dispatcher):
    dp.register_callback_query_handler(balance_start ,lambda callback_query: callback_query.data == "balance",state="*")


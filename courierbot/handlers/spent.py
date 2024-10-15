from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery
import re
from db import BotDBClass
from decimal import Decimal
import kb

BotDB=BotDBClass('db.db')


class OrderDelivery(StatesGroup):
    waiting_for_spent_category = State()
    waiting_for_spent_name = State()
    waiting_for_spent_sum = State()


# Обратите внимание: есть второй аргумент
async def spent_start(clbck: CallbackQuery,state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for name in BotDB.get_categories_names('s'):
        keyboard.add(name)
    await clbck.message.answer("Выберите категорию:", reply_markup=keyboard)
    await state.set_state(OrderSpent.waiting_for_spent_category.state)
async def spent_category_chosen(message: types.Message, state: FSMContext):
    await state.update_data(spent_category=message.text.capitalize())
    await state.set_state(OrderSpent.waiting_for_spent_name.state)
    await message.bot.send_message(message.chat.id,"Введите статью расходов:",reply_markup=types.ReplyKeyboardRemove())
async def spent_chosen(message: types.Message, state: FSMContext):
    await state.update_data(spent=message.text.capitalize())
    await state.set_state(OrderSpent.waiting_for_spent_sum.state)
    await message.bot.send_message(message.chat.id,"Введите сумму:")

async def spent_sum_chosen(message: types.Message, state: FSMContext):

    x = re.findall(r'\d+(?:.\d+)?', message.text.lower())
    if (len(x)):
        value = "{0:.2f}".format(Decimal(x[0].replace(',', '.')))
    else:
       await message.answer("Пожалуйста, правильно введите сумму.")
       return

    await state.update_data(spent_sum=float(value))
    user_data = await state.get_data()
    BotDB.add_record(message.from_user.id, user_data['spent_category'],user_data['spent'],user_data['spent_sum'],'s')
    BotDB.change_balance(message.from_user.id,-user_data['spent_sum'])



    await message.answer(f"Вы внесли в расходы сумму {value}  по статье {user_data['spent'].capitalize()} "
     f"категории {user_data['spent_category']}.\n Баланс пользователя:" '{0:.2f}'.format(BotDB.get_user_balance(message.from_user.id)))
    await message.bot.send_message(message.from_user.id,
                                   f"Выберите действие в меню",
                                   reply_markup=kb.menu)
    await state.finish()
def register_handlers_spent(dp: Dispatcher):
    dp.register_callback_query_handler(spent_start ,lambda callback_query: callback_query.data == "spent",state="*")
    #dp.register_message_handler(spent_start, commands="spent", state="*")
    dp.register_message_handler(spent_category_chosen, state=OrderSpent.waiting_for_spent_category)
    dp.register_message_handler(spent_chosen, state=OrderSpent.waiting_for_spent_name)
    dp.register_message_handler(spent_sum_chosen, state=OrderSpent.waiting_for_spent_sum)

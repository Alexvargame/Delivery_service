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


class OrderDelivery(StatesGroup):
    waiting_for_delivery_number = State()
    waiting_for_change_delivery_status = State()
    waiting_for_spent_sum = State()


# Обратите внимание: есть второй аргумент
async def delivery_start(clbck: CallbackQuery,state: FSMContext):

    deliveres=BotDB.get_deliveres_on_work(BotDB.get_user_id(clbck.message.chat.id))
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    BotDB.check_deliveres_on_waitnig(BotDB.get_user_id(clbck.message.chat.id))
    for delivery in BotDB.get_deliveres_on_work(BotDB.get_user_id(clbck.message.chat.id)):
        keyboard.add(str(delivery[9]))
    keyboard.add('Отмена')
    await clbck.message.answer("Выберите доставку:", reply_markup=keyboard)
    await state.set_state(OrderDelivery.waiting_for_delivery_number.state)


async def delivery_info(message: types.Message, state: FSMContext):
    await state.update_data(delivery_number=message.text)
    if message.text!='Отмена':
        delivery=BotDB.get_delivery(message.text)

        await message.answer(f"Информация о заказе:\n"
                            f"Номер-{delivery[9]}\n"
                            f"Заказчик-{BotDB.get_user(delivery[7])[4]}\n"
                             f"Принят в работу-{delivery[11]}\n"
                             f"Срок доставки-{delivery[10]}\n"
                             f"Адресс доставки-{' '.join(BotDB.get_delivery_point(delivery[8]))}\n"
                             f"Стоимости доставки-{delivery[1]}\n"
                             f"Статус-{delivery[4]}\n")
        await message.bot.send_message(message.from_user.id,f"Изменить статус?",reply_markup=courierbot.kb.menu_delivery_info)
        await state.set_state(OrderDelivery.waiting_for_change_delivery_status.state)
    else:
        await state.finish()
        await message.answer("Действие отменено", reply_markup=types.ReplyKeyboardRemove())
        await message.bot.send_message(message.from_user.id,
                                       "Выберите действие в меню",
                                       reply_markup=courierbot.kb.menu)


async  def change_delivery_status (message: types.Message, state: FSMContext):
    await state.update_data(change=message.text)
    user_data=await state.get_data()
    if message.text == '📝 Доставлено':
        status='delivered'
        BotDB.change_delivery_status(user_data['delivery_number'],'delivered')
        print(BotDB.get_delivery(user_data['delivery_number'])[1])
        BotDB.change_balance(BotDB.get_user_id(message.chat.id),BotDB.get_delivery(user_data['delivery_number'])[1])

        await message.answer(f"Статус доставки изменен на {status}", reply_markup=types.ReplyKeyboardRemove())

    else:
        await message.answer(f"Статус доставки остался on_work", reply_markup=types.ReplyKeyboardRemove())
    deliveres = BotDB.get_deliveres_on_work(BotDB.get_user_id(message.chat.id))
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for delivery in BotDB.get_deliveres_on_work(BotDB.get_user_id(message.chat.id)):
        keyboard.add(str(delivery[9]))
    keyboard.add('Отмена')
    await message.answer("Выберите доставку:", reply_markup=keyboard)
    await state.set_state(OrderDelivery.waiting_for_delivery_number.state)



def register_handlers_delivery(dp: Dispatcher):
    dp.register_callback_query_handler(delivery_start ,lambda callback_query: callback_query.data == "delivery",state="*")

    dp.register_message_handler(delivery_info, state=OrderDelivery.waiting_for_delivery_number)
    dp.register_message_handler(change_delivery_status, state=OrderDelivery.waiting_for_change_delivery_status)
    # dp.register_message_handler(spent_sum_chosen, state=OrderSpent.waiting_for_spent_sum)

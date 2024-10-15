from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery
import aiogram.utils.markdown as fmt
import re
import os
import json
from datetime import timedelta,date,datetime
from courierbot.db import BotDBClass
import courierbot.kb
from decimal import Decimal

from pathlib import Path

#from  .delivery import OrderDelivery

BotDB=BotDBClass(Path(__file__).resolve().parent.parent.parent/'db.sqlite3')

available_report_types = ["Доставки", "Инфо","Выбрать отчет"]
available_report_deliveres_types=['Выполненные','В ожидании','Отмененные']
available_report_info=['Заказчики','Адреса','Другое']
available_report_periods = ["День","Неделя", "Месяц","Всего"]
report={}
report_info={}
class OrderReport(StatesGroup):
    waiting_for_type_report = State()
    waiting_for_report_deliveres_types = State()
    waiting_for_delivery_number=State()
    waiting_for_report_info = State()
    waiting_for_period = State()
    waiting_for_back_to_menu=State()
    waiting_for_save=State()



# Обратите внимание: есть второй аргумент
async def report_start(clbck: CallbackQuery, state: FSMContext):

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for name in available_report_types:
        keyboard.add(name)
    await clbck.message.answer("Выберите тип отчета:", reply_markup=keyboard)
    await state.set_state(OrderReport.waiting_for_type_report.state)

async def report_category_chosen(message: types.Message, state: FSMContext):
    if message.text.capitalize()=='Доставки':
        await state.update_data(report_type=message.text.capitalize())
        await state.set_state(OrderReport.waiting_for_report_deliveres_types.state)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for name in available_report_deliveres_types:
            keyboard.add(name)
        keyboard.add('Отмена')
        await message.bot.send_message(message.chat.id,"Выберите пункт меню:", reply_markup=keyboard)
    elif message.text.capitalize()=='Инфо':
        await state.update_data(report_type=message.text.capitalize())
        await state.set_state(OrderReport.waiting_for_report_info.state)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for name in available_report_info:
            keyboard.add(name)
        keyboard.add('Отмена')
        await message.bot.send_message(message.chat.id,"Выберите пункт меню:", reply_markup=keyboard)
    elif message.text.capitalize()=='Выбрать отчет':
        pass
        # await state.update_data(report_type=message.text.capitalize())
        # await state.set_state(OrderReport.waiting_for_open_report.state)
        # for file in [f for f in os.listdir() if f.startswith('report')]:
        #     file_newname = os.path.join("C:\Python39\SpentCostBot", file)
        #     await message.bot.send_message(message.chat.id,file,parse_mode='HTML')
        # await message.answer("Выберите файл", reply_markup=types.ReplyKeyboardRemove())





async def category_delivery_chosen(message: types.Message, state: FSMContext):
    print(message.text)
    await state.update_data(delivery_category=message.text.capitalize())
    if message.text.capitalize()=='Выполненные':
        await state.update_data(delivery_category='delivered')
        data = await state.get_data()
        await state.set_state(OrderReport.waiting_for_period.state)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for name in available_report_periods:
            keyboard.add(name)
        keyboard.add('Отмена')
        await message.bot.send_message(message.chat.id, "Выберите период времени :", reply_markup=keyboard)
        await state.set_state(OrderReport.waiting_for_period)
    elif message.text.capitalize()=='Отмененные':
        await state.update_data(delivery_category='canceled')
        data = await state.get_data()
        await state.set_state(OrderReport.waiting_for_period.state)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for name in available_report_periods:
            keyboard.add(name)
        keyboard.add('Отмена')
        await message.bot.send_message(message.chat.id, "Выберите период времени :", reply_markup=keyboard)
        await state.set_state(OrderReport.waiting_for_period)
    elif message.text.capitalize()=='В ожидании':
        await state.update_data(delivery_category='waiting')
        data = await state.get_data()
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for delivery in BotDB.get_deliveres_on_status(BotDB.get_user_id(message.chat.id),data['delivery_category']):
            keyboard.add(str(delivery[9]))
        keyboard.add('Отмена')
        await message.bot.send_message(message.chat.id, "Выберите доставку :", reply_markup=keyboard)
        await state.set_state(OrderReport.waiting_for_delivery_number.state)
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for name in available_report_types:
            keyboard.add(name)
        await message.answer("Выберите тип отчета:", reply_markup=keyboard)
        await state.set_state(OrderReport.waiting_for_type_report.state)


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
        await message.bot.send_message(message.from_user.id, f"Дальше?",
                                       reply_markup=courierbot.kb.menu_delivery_info_report)
        await state.set_state(OrderReport.waiting_for_back_to_menu.state)
    else:
        await state.update_data(report_type=message.text.capitalize())
        await state.set_state(OrderReport.waiting_for_report_deliveres_types.state)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for name in available_report_deliveres_types:
            keyboard.add(name)
        keyboard.add('Отмена')
        await message.bot.send_message(message.chat.id, "Выберите пункт меню:", reply_markup=keyboard)
        # deliveres = BotDB.get_deliveres_on_work(BotDB.get_user_id(message.chat.id))
        # keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        # for delivery in BotDB.get_deliveres_on_status(BotDB.get_user_id(message.chat.id),'waiting'):
        #     keyboard.add(str(delivery[9]))
        # keyboard.add('Отмена')
        # await message.answer("Выберите доставку:", reply_markup=keyboard)
        # #await state.set_state(OrderReport.waiting_for_delivery_number.state)

async  def back_to_menu (message: types.Message, state: FSMContext):
    await state.update_data(change=message.text)
    data=await state.get_data()
    print(data)
    if message.text == 'Назад к списку':
        if data['report_type']=='Доставки':
            await state.update_data(delivery_category=message.text.capitalize())
            data = await state.get_data()
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for delivery in BotDB.get_deliveres_on_status(BotDB.get_user_id(message.chat.id),'waiting'):
                keyboard.add(str(delivery[9]))
            keyboard.add('Отмена')
            await message.bot.send_message(message.chat.id, "Выберите доставку :", reply_markup=keyboard)
            await state.set_state(OrderReport.waiting_for_delivery_number.state)
        elif data['report_type']=='Инфо':
            await state.set_state(OrderReport.waiting_for_report_info.state)
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for name in available_report_info:
                keyboard.add(name)
            keyboard.add('Отмена')
            await message.bot.send_message(message.chat.id, "Выберите пункт меню:", reply_markup=keyboard)
    else:
        if data['report_type'] == 'Доставки':
            await state.update_data(report_type=message.text.capitalize())
            await state.set_state(OrderReport.waiting_for_report_deliveres_types.state)
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for name in available_report_deliveres_types:
                keyboard.add(name)
            keyboard.add('Отмена')
            await message.bot.send_message(message.chat.id, "Выберите пункт меню:", reply_markup=keyboard)
        elif data['report_type'] == 'Инфо':
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for name in available_report_types:
                keyboard.add(name)
            await message.answer("Выберите тип отчета:", reply_markup=keyboard)
            await state.set_state(OrderReport.waiting_for_type_report.state)





async def report_for_info(message: types.Message, state: FSMContext):
    global report_info

    await state.update_data(category_info=message.text.capitalize())
    data = await state.get_data()
    report = BotDB.get_report_info(BotDB.get_user_id(message.chat.id), data['category_info'])
    print(report)
    if data['category_info']=='Заказчики':
        for rep in report:
            key,value=BotDB.get_user(rep[0]),report.count(rep)
            report_info[key]=value
        for key, value in report_info.items():
            await message.answer(f"Заказчик {key[4]} Кол-во заказов {value}")
    elif data['category_info']=='Адреса':
        for rep in report:
            key, value = BotDB.get_delivery_point(rep[0]), report.count(rep)
            report_info[key] = value
        for key, value in report_info.items():
            await message.answer(f"Адрес {key[0]},{key[1]},{key[2]},{key[3]},{key[4]} Кол-во заказов {value}")

    await message.bot.send_message(message.from_user.id, f"Дальше?",
                                       reply_markup=courierbot.kb.menu_delivery_info_report)
    await state.set_state(OrderReport.waiting_for_back_to_menu.state)
    #await state.set_state(OrderReport.waiting_for_category.state)


    # report=BotDB.get_reports(message.from_user.id,data['report_type'],data['report_category'],data['category_category'])
    # print(report)
    # await message.answer(f"Тип отчета: {data['report_type']}\n Категория: {data['category_category']}")
    # for rep in report:
    #     await message.answer(f"Статья: {rep[0]}\n Cумма:  {rep[1]}\n Дата: {rep[2].split()[0]}")
    # markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # save = types.KeyboardButton('Сохранить')
    # not_save=types.KeyboardButton('Не сохранять')
    # markup.add(save,not_save)
    # await message.bot.send_message(message.chat.id, "Сохранить отчет?", reply_markup=markup)
    # await state.set_state(OrderReport.waiting_for_save.state)





async def report_time_period(message: types.Message, state: FSMContext):

        global report
        if message.text.capitalize()!='Отмена':
            await state.update_data(period=message.text.capitalize())
            await state.set_state(OrderReport.waiting_for_period.state)
            data = await state.get_data()
            report=BotDB.get_period_reports(BotDB.get_user_id(message.chat.id),data['delivery_category'],message.text.capitalize())
            await message.answer(f"Тип отчета: {data['delivery_category']}\n Период: {data['period']}")
            print(report)
            counts_report = len(report)
            sum_report = sum([rep[1] for rep in report])
            for delivery in report:
                await message.answer(f"Информация о заказе:\n"
                                     f"Номер-{delivery[9]}\n"
                                     f"Заказчик-{BotDB.get_user(delivery[7])[4]}\n"
                                     f"Принят в работу-{delivery[11]}\n"
                                     f"Срок доставки-{delivery[10]}\n"
                                     f"Адресс доставки-{' '.join(BotDB.get_delivery_point(delivery[8]))}\n"
                                     f"Стоимости доставки-{delivery[1]}\n"
                                     f"Статус-{delivery[4]}\n")
            await message.answer(f"Всего {counts_report} доставок на сумму {sum_report}")
            report.append(counts_report)
            report.append(sum_report)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            save = types.KeyboardButton('Сохранить')
            not_save = types.KeyboardButton('Не сохранять')
            markup.add(save, not_save)
            await message.bot.send_message(message.chat.id, "Сохранить отчет?", reply_markup=markup)
            await state.set_state(OrderReport.waiting_for_save.state)
        else:
            await state.update_data(report_type=message.text.capitalize())
            await state.set_state(OrderReport.waiting_for_report_deliveres_types.state)
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for name in available_report_deliveres_types:
                keyboard.add(name)
            keyboard.add('Отмена')
            await message.bot.send_message(message.chat.id, "Выберите пункт меню:", reply_markup=keyboard)



async  def report_save(message: types.Message, state: FSMContext):
    await state.update_data(save=message.text.capitalize())
    NAME_FILE = 'report_category' + str(datetime.now())[:10] + '_' + str(datetime.now())[11:19].replace(':', '-',
                                                                                                        2) + '.json'
    if message.text == 'Сохранить':
        with open(NAME_FILE, 'w') as f:
            json.dump(report, f)
        await message.answer("Сохранено", reply_markup=types.ReplyKeyboardRemove())
        await message.bot.send_document(message.chat.id, document=open(NAME_FILE, 'rb'))
        await state.finish()

    else:
        #await message.answer("Не сохранено", reply_markup=types.ReplyKeyboardRemove())
        await state.finish()

    await message.bot.send_message(message.from_user.id,
                                   f"Выберите действие в меню",
                                   reply_markup=courierbot.kb.menu)


def register_handlers_reports(dp: Dispatcher):
    dp.register_callback_query_handler(report_start, lambda callback_query: callback_query.data == "reports", state="*")
    #dp.register_message_handler(report_start, commands="reports", state="*")
    dp.register_message_handler(report_category_chosen, state=OrderReport.waiting_for_type_report)
    dp.register_message_handler(category_delivery_chosen, state=OrderReport.waiting_for_report_deliveres_types)
    dp.register_message_handler(delivery_info, state=OrderReport.waiting_for_delivery_number)
    dp.register_message_handler(back_to_menu,state=OrderReport.waiting_for_back_to_menu)
    dp.register_message_handler(report_for_info, state=OrderReport.waiting_for_report_info)
    dp.register_message_handler(report_time_period, state=OrderReport.waiting_for_period)
    dp.register_message_handler(report_save, state=OrderReport.waiting_for_save)

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
menu = [
    [InlineKeyboardButton(text="📝 Мои доставки", callback_data="delivery"),
    InlineKeyboardButton(text="🖼 Добавить поступления", callback_data="auth_reg")],
    [InlineKeyboardButton(text="💳 Отчеты", callback_data="reports"),
    InlineKeyboardButton(text="💰 Поиск", callback_data="search")],
    [InlineKeyboardButton(text="💎 Баланс пользователя", callback_data="balance"),
    InlineKeyboardButton(text="🎁 Отмена", callback_data="cancel")],
]
menu = InlineKeyboardMarkup(inline_keyboard=menu)
exit_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="◀️ Выйти в меню")]], resize_keyboard=True)
iexit_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Выйти в меню", callback_data="menu")]])

menu_delivery_info = [
    [KeyboardButton("📝 Доставлено"),
    KeyboardButton("🎁 Назад к списку")]
]
menu_delivery_info = ReplyKeyboardMarkup(menu_delivery_info,resize_keyboard=True)

menu_delivery_info_report = [
    [KeyboardButton("Назад к списку"),
    KeyboardButton("Отмена")]
]
menu_delivery_info_report = ReplyKeyboardMarkup(menu_delivery_info_report,resize_keyboard=True)
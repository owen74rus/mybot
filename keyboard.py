from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ContentTypes


inline_btn_1 = InlineKeyboardButton('Пакет Standart', callback_data='Standart')
inline_kb1 = InlineKeyboardMarkup().add(inline_btn_1)
inline_btn_2 = InlineKeyboardButton('Пакет Premium', callback_data='Premium')
inline_kb2 = InlineKeyboardMarkup().add(inline_btn_2)
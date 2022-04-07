import asyncio
import types
import re
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import ContentTypes
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import configdb
import keyboard
from config import TOKEN, PRICE, PRICE1, PAYMENTS_PROVIDER_TOKEN, all_members_are_administrators

loop = asyncio.get_event_loop()
bot = Bot(token=TOKEN)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage, loop=loop)
TIME_MACHINE_IMAGE_URL = 'https://static.tildacdn.com/tild3963-3835-4430-b431-313939613737/IMG_1496.JPG'
available_time = ["12:00", "14:00", "16:00"]
used_date = list
used_time = list


class Reg(StatesGroup):
    name = State()
    instagram_name = State()
    phone_num = State()
    reg_date = State()
    reg_time = State()


class State1(StatesGroup):
    buy_standart = State()
    buy_premium = State()


@dp.message_handler(CommandStart(), state="*")
async def name_step(message: types.Message):
    await message.answer(text="Добрый день! Сейчас мы с Вами за несколько шагов зарезервируем за "
                              "Вами место на консультацию.")
    await message.answer(text='Напишите Ваше имя ')
    await Reg.name.set()


@dp.message_handler(state=Reg.name, content_types=types.ContentTypes.TEXT)
async def inst_step(message: types.Message, state: FSMContext):
    user_name = message.text
    if not re.search("^[а-яА-Яa-zA-Z]{1,30}$", user_name):
        await message.reply("Неверный формат имени. Попробуйте ещё раз. Имя должно быть на латинице или кириллице")
        return
    await state.update_data(name_user=message.text.title())
    await message.answer(text='Напишите свой ник в instagram')
    await Reg.instagram_name.set()


@dp.message_handler(state=Reg.instagram_name, content_types=types.ContentTypes.TEXT)
async def phone_step(message: types.Message, state: FSMContext):
    inst_data = message.text
    if not re.search("^[a-zA-Z0-9_.@]{1,30}$", inst_data):
        await message.reply("Неверный формат инстраграм-ника. Попробуйте ещё раз.")
        return
    await state.update_data(inst_user=message.text.title())
    await message.answer(text='Напишите свой номер телефона, который привязан к телеграмм')
    await Reg.phone_num.set()


@dp.message_handler(state=Reg.phone_num, content_types=types.ContentTypes.TEXT)
async def date_step(message: types.Message, state: FSMContext):
    number_user = message.text
    if not re.search("^\+?[1-9][-\(]?\d{3}\)?-?\d{3}-?\d{2}-?\d{2}$", number_user):
        await message.reply("Неверный формат номера телефона. Попробуйте ещё раз.")
        return
    await state.update_data(phone=message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    result_date = await configdb.sql_select_freedate(message.text)
    for name in result_date:
        keyboard.add(name)
    await message.answer(text='Доступные даты для записи:', reply_markup=keyboard)
    await Reg.reg_date.set()


@dp.message_handler(state=Reg.reg_date, content_types=types.ContentTypes.TEXT)
async def time_step(message: types.Message, state: FSMContext):
    result_date = await configdb.sql_select_freedate(message.text)
    if message.text.lower() not in result_date:
        await message.answer("пожалуйта выберете дату используя клавиатуру ниже.")
        return
    await state.update_data(date=message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for name in available_time:
        keyboard.add(name)
    await message.answer(text='Доступное время для записи:', reply_markup=keyboard)
    await Reg.reg_time.set()


@dp.message_handler(state=Reg.reg_time, content_types=types.ContentTypes.TEXT)
async def buy_step(message: types.Message, state: FSMContext):
    if message.text.lower() not in available_time:
        await message.answer("Пожалуйта выберете время используя клавиатуру нижe")
        return
    await state.update_data(reg_time=message.text)
    await message.answer(text='Теперь Вы можете выбрать пакет консультации и сразу оплатить место  \n '
                              'подробное описание пакетов доступно по ссылке: https://ohhenkel.ru/consultation:',
                         reply_markup=types.ReplyKeyboardRemove())
    await message.answer("Купить пакет Standart:", reply_markup=keyboard.inline_kb1)
    await message.answer("Купить пакет Premium:", reply_markup=keyboard.inline_kb2)
    configdb.USER_DATA = await state.get_data()
    await state.finish()


@dp.callback_query_handler(lambda c: c.data == 'Standart')
async def callback_query_button1(callback_query: types.CallbackQuery):
    configdb.USER_ID = callback_query.from_user
    configdb.USER_PACK = "Standart"
    await bot.send_invoice(chat_id=callback_query.from_user.id,
                           title='пакет Standart',
                           provider_token=PAYMENTS_PROVIDER_TOKEN,
                           description='Длительность консультации 1-1,5 часа \n Вы получите ответы на все волнующие Вас'
                                       'вопросы \n Важно! После консультации нет обратной связи',
                           currency='rub',
                           need_email=True,
                           send_email_to_provider=True,
                           # photo_url=TIME_MACHINE_IMAGE_URL,
                           # photo_height=512,  # !=0/None, иначе изображение не покажется
                           # photo_width=512,
                           # photo_size=512,
                           # is_flexible=False,  # True если конечная цена зависит от способа доставки
                           prices=[PRICE],
                           payload='some-invoice-payload-for-our-internal-use')
    await bot.send_message(text='Если вы хотите Выбрать тариф Premium нажмите кнопку:',
                           reply_markup=keyboard.inline_kb2,
                           chat_id=callback_query.from_user.id)


@dp.callback_query_handler(lambda c: c.data == 'Premium')
async def callback_query_button2(callback_query: types.CallbackQuery):
    configdb.USER_ID = callback_query.from_user
    configdb.USER_PACK = "Premium"
    await bot.send_invoice(chat_id=callback_query.from_user.id,
                           title='пакет Premium',
                           provider_token=PAYMENTS_PROVIDER_TOKEN,
                           description='Длительность консультации 1-1,5 часа \n Вы получите ответы на все волнующие Вас'
                                       'вопросы \n Обратная связь после консультации в течении 7 дней \n'
                                       'Распаковка личности + создание карты по сторис \n Проверка Д/З'
                                       ' и работа над ошибками ',
                           currency='rub',
                           need_email=True,
                           send_email_to_provider=True,
                           # photo_url=TIME_MACHINE_IMAGE_URL,
                           # photo_height=512,  # !=0/None, иначе изображение не покажется
                           # photo_width=512,
                           # photo_size=512,
                           # is_flexible=False,  # True если конечная цена зависит от способа доставки
                           prices=[PRICE1],
                           payload='some-invoice-payload-for-our-internal-use')
    await bot.send_message(text='Если вы хотите Выбрать тариф Standart нажмите кнопку:',
                           reply_markup=keyboard.inline_kb1,
                           chat_id=callback_query.from_user.id)


@dp.pre_checkout_query_handler(lambda query: True)
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message_handler(content_types=ContentTypes.SUCCESSFUL_PAYMENT)
async def got_payment(message: types.Message):
    if message.successful_payment.total_amount == 100000:
        await bot.send_message(message.chat.id, 'Вы успешно оплатили и зарезервировали место на консультацию.\n'
                                                'За 2 дня необходимо прислать вопросы, которые вас интересуют, с них '
                                                'начнём консультацию. \n'
                                                'Прислать вопросы можно в телеграм (мой ник ohhenkel)  '
                               .format(message.successful_payment.total_amount / 100, message.successful_payment.
                                       currency), parse_mode='Markdown')
    else:
        await bot.send_message(message.chat.id, 'Вы успешно оплатили и зарезервировали место на консультацию.\n '
                                                'За 3 дня необходимо прислать вопросы, которые вас интересуют, с них '
                                                'начнём консультацию. \n'
                                                '\b Прислать вопросы можно в телеграм (мой ник ohhenkel) \n'
                                                'Отдельно необходимо заполнить бриф для распаковки личности - на '
                                                'основании него я буду строить карту по сторис, карта составляется'
                                                ' в течение 7-9 рабочих дней после консультации) \n '
                                                'https://docs.google.com/forms/d/1JWyTd7piGFu2QfTywjz-41EpKRkTSg2f9qC1D'
                                                'XazRsk/edit'
                               .format(message.successful_payment.total_amount / 100,
                                       message.successful_payment.currency),
                               parse_mode='Markdown')
    await bot.send_message(all_members_are_administrators, f'{configdb.USER_DATA}{configdb.USER_PACK}')
    await configdb.sql_add_command(configdb.USER_DATA, configdb.USER_ID, configdb.USER_PACK)
    await configdb.sql_replace_commands(configdb.USER_DATA)


@dp.message_handler(commands="add_date", state="*")
async def add_data(message: types.Message):
    adm = all_members_are_administrators
    if message.chat.id not in adm:
        await bot.send_message(message.chat.id, 'Не дозволено')
    else:
        await bot.send_message(message.chat.id, 'введите доступные даты')


if __name__ == '__main__':
    executor.start_polling(dp, loop=loop)

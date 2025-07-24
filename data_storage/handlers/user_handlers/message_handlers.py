import html

from aiogram import Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from utils.functions import add_user_document, add_user_photo, add_user_audio, add_user_voice, \
    get_file, get_user_sounds, is_voice

from states.user import UserState


async def start_command(message: types.Message) -> None:
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(text='Загрузить файл', callback_data='load')],
                         [types.InlineKeyboardButton(text='Получить файл', callback_data='get')]])
    await message.answer(f"<b>{html.escape(message.from_user.full_name)},</b> я могу хранить твои файлы.\n\n"
                         f"Ты можешь выбрать, какой тип файла ты хочешь мне загрузить,\nя назначу ему ID\n\n"
                         f"Если ты напишешь мне назначенный ID,\nя отправлю тебе этот файл",
                         reply_markup=kb)


async def random_message_handler(message: types.Message) -> None:
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(text='Загрузить файл', callback_data='load')],
                         [types.InlineKeyboardButton(text='Получить файл', callback_data='get')]])
    await message.answer(f"Извини, я не понимаю чего ты хочешь, вот что я умею:\n\n"
                         f"<b>{html.escape(message.from_user.full_name)},</b> я могу хранить твои файлы.\n\n"
                         f"Ты можешь выбрать, какой тип файла ты хочешь мне загрузить,\nя назначу ему ID\n\n"
                         f"Если ты напишешь мне назначенный ID,\nя отправлю тебе этот файл",
                         reply_markup=kb)


async def document_handler(message: types.Message, state: FSMContext) -> None:
    kb1 = types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(text='В меню', callback_data='menu')]])
    kb2 = types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(text='Назад', callback_data='choose')]])
    if message.document:
        await add_user_document(message.from_user.id, message.from_user.username, message.from_user.full_name,
                                message.document.file_id)
        await message.answer("Ваш файл успешно записан в базу данных!", reply_markup=kb1)
        await state.set_state(state=None)
    else:
        await message.answer("Ваш тип файла не соответствует выбранному! Отправьте документ!", reply_markup=kb2)


async def photo_handler(message: types.Message, state: FSMContext) -> None:
    kb1 = types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(text='В меню', callback_data='menu')]])
    kb2 = types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(text='Назад', callback_data='choose')]])
    if message.photo:
        await add_user_photo(message.from_user.id, message.from_user.username, message.from_user.full_name,
                             message.photo[-1].file_id)
        await message.answer("Ваше фото успешно записано в базу данных!", reply_markup=kb1)
        await state.set_state(state=None)
    else:
        await message.answer("Ваш тип файла не соответствует выбранному! Отправьте фото!", reply_markup=kb2)


async def audio_handler(message: types.Message, state: FSMContext) -> None:
    kb1 = types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(text='В меню', callback_data='menu')]])
    kb2 = types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(text='Назад', callback_data='choose')]])
    if message.voice or message.audio:
        if message.voice:
            await add_user_voice(message.from_user.id, message.from_user.username, message.from_user.full_name,
                                 message.voice.file_id)
        else:
            await add_user_audio(message.from_user.id, message.from_user.username, message.from_user.full_name,
                                 message.audio.file_id)
        await message.answer("Ваше аудио успешно записано в базу данных!", reply_markup=kb1)
        await state.set_state(state=None)
    else:
        await message.answer("Ваш тип файла не соответствует выбранному! Отправьте аудио!", reply_markup=kb2)


# ==================================================================================
async def get_photo_handler(message: types.Message, state: FSMContext) -> None:
    kb = types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(text='В меню', callback_data='menu')]])
    try:
        await state.update_data(photo_id=int(message.text))
        data = await state.get_data()
        photo_id = data['photo_id']
        tg_photo_id = await get_file(photo_id)
        await message.answer_photo(tg_photo_id)
        await message.answer("Нажми на кнопку, чтобы вернуться в меню", reply_markup=kb)
    except ValueError:
        await message.answer("Неверно набранный ID, попробуй еще раз.\nИли нажми кнопку внизу, чтобы вернуться в меню",
                             reply_markup=kb)


async def get_doc_handler(message: types.Message, state: FSMContext) -> None:
    kb = types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(text='В меню', callback_data='menu')]])
    try:
        await state.update_data(doc_id=int(message.text))
        data = await state.get_data()
        doc_id = data['doc_id']
        tg_doc_id = await get_file(doc_id)
        await message.answer_document(tg_doc_id)
        await message.answer("Нажми на кнопку, чтобы вернуться в меню", reply_markup=kb)
    except ValueError:
        await message.answer("Неверно набранный ID, попробуй еще раз.\nИли нажми кнопку внизу, чтобы вернуться в меню",
                             reply_markup=kb)


async def get_audio_handler(message: types.Message, state: FSMContext) -> None:
    kb = types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(text='В меню', callback_data='menu')]])
    try:
        await state.update_data(audio_id=int(message.text))
        data = await state.get_data()
        audio_id = data['audio_id']
        tg_audio_id = await get_file(audio_id)
        if await is_voice(audio_id):
            await message.answer_voice(tg_audio_id)
        else:
            await message.answer_audio(tg_audio_id)
        await message.answer("Нажми на кнопку, чтобы вернуться в меню", reply_markup=kb)
    except ValueError:
        await message.answer("Неверно набранный ID, попробуй еще раз.\nИли нажми кнопку внизу, чтобы вернуться в меню",
                             reply_markup=kb)


def register_user_message_handler(dp: Dispatcher):
    dp.message.register(start_command, CommandStart())
    dp.message.register(document_handler, UserState.document)
    dp.message.register(photo_handler, UserState.photo)
    dp.message.register(audio_handler, UserState.audio)
    dp.message.register(get_photo_handler, UserState.get_photo)
    dp.message.register(get_doc_handler, UserState.get_doc)
    dp.message.register(get_audio_handler, UserState.get_audio)
    dp.message.register(random_message_handler)

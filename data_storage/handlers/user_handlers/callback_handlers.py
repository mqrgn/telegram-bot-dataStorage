import html

from aiogram import Dispatcher, types, F
from aiogram.fsm.context import FSMContext

from utils.functions import get_user_photos, get_user_docs, get_user_sounds, create_pagination_kb, \
    get_file
from states.user import UserState
from utils.paginator import DatabasePaginator


async def callback_load_handler(callback: types.CallbackQuery) -> None:
    kb = types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(text='Документ', callback_data='doc')],
                                                     [types.InlineKeyboardButton(text='Фото', callback_data='photo')],
                                                     [types.InlineKeyboardButton(text='Аудио', callback_data='audio')],
                                                     [types.InlineKeyboardButton(text='Назад', callback_data='menu')]])
    await callback.message.edit_text("Выберите тип файла, который хотите загрузить: ", reply_markup=kb)
    await callback.answer()


async def callback_doc_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(text='Назад', callback_data='load')]])
    await state.set_state(UserState.document)
    await callback.message.edit_text("Отправьте документ, который хотите загрузить в базу: ", reply_markup=kb)
    await callback.answer()


async def callback_photo_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(text='Назад', callback_data='load')]])
    await state.set_state(UserState.photo)
    await callback.message.edit_text("Отправьте фото, которое хотите загрузить в базу: ", reply_markup=kb)


async def callback_audio_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(text='Назад', callback_data='load')]])
    await state.set_state(UserState.audio)
    await callback.message.edit_text("Отправьте аудио, которое хотите загрузить в базу: ", reply_markup=kb)


async def callback_choose_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    kb = types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(text='Документ', callback_data='doc')],
                                                     [types.InlineKeyboardButton(text='Фото', callback_data='photo')],
                                                     [types.InlineKeyboardButton(text='Аудио', callback_data='audio')],
                                                     [types.InlineKeyboardButton(text='Назад', callback_data='menu')]])
    await callback.message.edit_text("Выберите тип файла, который хотите загрузить: ", reply_markup=kb)


async def callback_menu_handler(callback: types.CallbackQuery) -> None:
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(text='Загрузить файл', callback_data='load')],
                         [types.InlineKeyboardButton(text='Получить файл', callback_data='get')]])
    await callback.message.edit_text(
        f"<b>{html.escape(callback.from_user.full_name)},</b> я могу хранить твои файлы.\n\n"
        f"Ты можешь выбрать какой тип файлов ты хочешь мне загрузить, я назначу ему ID\n"
        f"Если ты напишешь мне назначенный ID, я отправлю тебе этот файл", reply_markup=kb)
    await callback.answer()


# ===========================================================================
async def callback_get_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    kb = [[types.InlineKeyboardButton(text='Документы', callback_data='get_doc')],
          [types.InlineKeyboardButton(text='Фото', callback_data='get_photo')],
          [types.InlineKeyboardButton(text='Аудио', callback_data='get_audio')],
          [types.InlineKeyboardButton(text='Назад', callback_data='menu')]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    await callback.message.edit_text(
        f"<b>{html.escape(callback.from_user.full_name)},</b> по кнопкам ниже список загруженных вами файлов",
        reply_markup=keyboard)


async def callback_get_photo_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    await state.set_state(UserState.get_photo)

    data = await state.get_data()
    current_page = data.get("page", 0)

    paginator = DatabasePaginator(
        db_path="Data_Storage_DB.db",
        user_id=callback.from_user.id,
        items_per_page=4,
    )

    paginator.set_filters({"file_type": "photo"})
    await paginator.count_files()
    paginator.current_page = current_page
    await paginator._load_current_page()

    items = paginator.get_current_items()
    if not items:
        kb = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text='В меню', callback_data='get')]
        ])
        await callback.message.edit_text("Увы, вы ещё не загружали фото.", reply_markup=kb)
        return

    file_buttons = [
        types.InlineKeyboardButton(
            text=str(item['global_number']),
            callback_data=f"select_photo_{item['id']}"
        ) for item in items
    ]

    file_buttons_rows = [file_buttons[i:i + 4] for i in range(0, len(file_buttons), 4)]

    # Кнопки пагинации
    pagination_buttons = [
        types.InlineKeyboardButton(text=btn['text'], callback_data=btn['callback_data'])
        for btn in paginator.get_pagination_buttons()
    ]

    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        *file_buttons_rows,
        pagination_buttons,
        [types.InlineKeyboardButton(text="Назад", callback_data="get")]
    ])

    numbered_photos = "\n".join(f"{item['global_number']}. {item['id']}" for item in items)

    await callback.message.edit_text(
        f"Вот ID фоток, которые вы загружали:\n{numbered_photos}\n\n"
        f"Нажми на номер фото, чтобы получить его.",
        reply_markup=kb
    )


async def callback_get_doc_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    page = data.get('doc_page', 0)
    items_per_page = 4
    docs_id = [item[0] for item in await get_user_docs(callback.from_user.id)]
    total_items = len(docs_id)

    if total_items == 0:
        kb = types.InlineKeyboardMarkup(
            inline_keyboard=[[types.InlineKeyboardButton(text='В меню', callback_data='get')]]
        )
        await callback.message.edit_text("Увы, вы еще не загружали документов.", reply_markup=kb)
        return

    start = page * items_per_page
    end = start + items_per_page
    page_docs = docs_id[start:end]

    file_buttons = [
        types.InlineKeyboardButton(
            text=str(start + i + 1),
            callback_data=f"select_doc_{doc_id}"
        ) for i, doc_id in enumerate(page_docs)
    ]
    file_buttons_rows = [file_buttons]

    # Кнопки пагинации
    kb_pagination = create_pagination_kb(page, total_items, items_per_page)

    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        *file_buttons_rows,
        *kb_pagination.inline_keyboard,
        [types.InlineKeyboardButton(text="В меню", callback_data="get")]
    ])

    numbered_docs = '\n'.join(f'{start + i + 1}. {doc_id}' for i, doc_id in enumerate(page_docs))

    await state.set_state(UserState.get_doc)
    await callback.message.edit_text(
        f"Вот ID документов, которые вы загружали:\n{numbered_docs}\n\n"
        f"Нажми на номер документа, чтобы получить файл.",
        reply_markup=kb
    )


async def callback_get_audio_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    page = data.get('audio_page', 0)
    items_per_page = 4
    audio_files_id = [item[0] for item in await get_user_sounds(callback.from_user.id)]
    total_items = len(audio_files_id)

    if total_items == 0:
        kb = types.InlineKeyboardMarkup(
            inline_keyboard=[[types.InlineKeyboardButton(text='В меню', callback_data='get')]]
        )
        await callback.message.edit_text("Увы, вы еще не загружали аудио.", reply_markup=kb)
        return

    start = page * items_per_page
    end = start + items_per_page
    page_audios = audio_files_id[start:end]

    file_buttons = [
        types.InlineKeyboardButton(
            text=str(start + i + 1),
            callback_data=f"select_audio_{audio_id}"
        ) for i, audio_id in enumerate(page_audios)
    ]
    file_buttons_rows = [file_buttons]

    # Кнопки пагинации
    kb_pagination = create_pagination_kb(page, total_items, items_per_page)

    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        *file_buttons_rows,
        *kb_pagination.inline_keyboard,
        [types.InlineKeyboardButton(text="В меню", callback_data="get")]
    ])

    numbered_audios = '\n'.join(f'{start + i + 1}. {audio_id}' for i, audio_id in enumerate(page_audios))

    await state.set_state(UserState.get_audio)
    await callback.message.edit_text(
        f"Вот ID аудио-файлов, которые вы загружали:\n{numbered_audios}\n\n"
        f"Нажми на номер аудио, чтобы получить файл.",
        reply_markup=kb
    )


async def pagination_handler(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    data = await state.get_data()

    if current_state == UserState.get_doc:
        page = data.get('doc_page', 0)
        if callback.data == 'next_page':
            page += 1
        elif callback.data == 'prev_page':
            page = max(page - 1, 0)
        await state.update_data(doc_page=page)
        # Вызываем обновлённый хендлер документов
        await callback_get_doc_handler(callback, state)

    elif current_state == UserState.get_audio:
        page = data.get('audio_page', 0)
        if callback.data == 'next_page':
            page += 1
        elif callback.data == 'prev_page':
            page = max(page - 1, 0)
        await state.update_data(audio_page=page)
        # Вызываем обновлённый хендлер аудио
        await callback_get_audio_handler(callback, state)

    elif current_state == UserState.get_photo:
        page = data.get('photo_page', 0)
        if callback.data == 'next_page':
            page += 1
        elif callback.data == 'prev_page':
            page = max(page - 1, 0)
        await state.update_data(photo_page=page)


async def send_selected_photo_handler(callback: types.CallbackQuery):
    photo_id = callback.data[len('select_photo_'):]
    photo_file = await get_file(photo_id)

    if photo_file:
        await callback.message.answer_photo(photo_file)
        await callback.answer()
    else:
        await callback.answer("Файл не найден.", show_alert=True)


async def send_selected_audio_handler(callback: types.CallbackQuery):
    audio_id = callback.data[len('select_audio_'):]
    audio_file = await get_file(audio_id)

    if audio_file:
        await callback.message.answer_audio(audio_file)
        await callback.answer()
    else:
        await callback.answer("Файл не найден.", show_alert=True)


async def send_selected_doc_handler(callback: types.CallbackQuery):
    doc_id = callback.data[len('select_doc_'):]
    doc_file = await get_file(doc_id)

    if doc_file:
        await callback.message.answer_document(doc_file)
        await callback.answer()
    else:
        await callback.answer("Файл не найден.", show_alert=True)


def register_user_callback_handler(dp: Dispatcher):
    dp.callback_query.register(callback_load_handler, F.data == 'load')
    dp.callback_query.register(callback_doc_handler, F.data == 'doc')
    dp.callback_query.register(callback_photo_handler, F.data == 'photo')
    dp.callback_query.register(callback_audio_handler, F.data == 'audio')
    dp.callback_query.register(callback_choose_handler, F.data == 'choose')
    dp.callback_query.register(callback_menu_handler, F.data == 'menu')
    dp.callback_query.register(callback_get_handler, F.data == 'get')
    dp.callback_query.register(callback_get_photo_handler, F.data == 'get_photo')
    dp.callback_query.register(callback_get_doc_handler, F.data == 'get_doc')
    dp.callback_query.register(callback_get_audio_handler, F.data == 'get_audio')
    dp.callback_query.register(pagination_handler, F.data.in_({'next_page', 'prev_page'}))
    dp.callback_query.register(send_selected_photo_handler, lambda c: c.data and c.data.startswith('select_photo_'))
    dp.callback_query.register(send_selected_audio_handler, lambda c: c.data and c.data.startswith('select_audio_'))
    dp.callback_query.register(send_selected_doc_handler, lambda c: c.data and c.data.startswith('select_doc_'))

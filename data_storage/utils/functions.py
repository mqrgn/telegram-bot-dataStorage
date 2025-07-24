import aiosqlite
from aiogram import types


async def add_user_document(user_id, username, full_name, tg_file_id):
    connect = await aiosqlite.connect('Data_Storage_DB.db')
    cursor = await connect.cursor()
    await cursor.execute(
        'INSERT INTO user_files (username, full_name, user_id, tg_file_id, file_type) VALUES (?, ?, ?, ?, ?)',
        (username, full_name, user_id, tg_file_id, 'document'))
    await connect.commit()
    file_number = await cursor.execute('SELECT number FROM user_files WHERE tg_file_id = ?', (tg_file_id,))
    file_number = await file_number.fetchone()
    user_file_id = file_number[0] + user_id
    await cursor.execute('UPDATE user_files SET user_file_id = ? WHERE tg_file_id = ?', (user_file_id, tg_file_id))
    await connect.commit()
    await cursor.close()
    await connect.close()


async def add_user_photo(user_id, username, full_name, tg_file_id):
    connect = await aiosqlite.connect('Data_Storage_DB.db')
    cursor = await connect.cursor()
    await cursor.execute(
        'INSERT INTO user_files (username, full_name, user_id, tg_file_id, file_type) VALUES (?, ?, ?, ?, ?)',
        (username, full_name, user_id, tg_file_id, 'photo'))
    await connect.commit()
    file_number = await cursor.execute('SELECT number FROM user_files WHERE tg_file_id = ?', (tg_file_id,))
    file_number = await file_number.fetchone()
    user_file_id = file_number[0] + user_id
    await cursor.execute('UPDATE user_files SET user_file_id = ? WHERE tg_file_id = ?', (user_file_id, tg_file_id))
    await connect.commit()
    await cursor.close()
    await connect.close()


async def add_user_voice(user_id, username, full_name, tg_file_id):
    connect = await aiosqlite.connect('Data_Storage_DB.db')
    cursor = await connect.cursor()
    await cursor.execute(
        'INSERT INTO user_files (username, full_name, user_id, tg_file_id, file_type) VALUES (?, ?, ?, ?, ?)',
        (username, full_name, user_id, tg_file_id, 'voice'))
    await connect.commit()
    file_number = await cursor.execute('SELECT number FROM user_files WHERE tg_file_id = ?', (tg_file_id,))
    file_number = await file_number.fetchone()
    user_file_id = file_number[0] + user_id
    await cursor.execute('UPDATE user_files SET user_file_id = ? WHERE tg_file_id = ?', (user_file_id, tg_file_id))
    await connect.commit()
    await cursor.close()
    await connect.close()


async def add_user_audio(user_id, username, full_name, tg_file_id):
    connect = await aiosqlite.connect('Data_Storage_DB.db')
    cursor = await connect.cursor()
    await cursor.execute(
        'INSERT INTO user_files (username, full_name, user_id, tg_file_id, file_type) VALUES (?, ?, ?, ?, ?)',
        (username, full_name, user_id, tg_file_id, 'audio'))
    await connect.commit()
    file_number = await cursor.execute('SELECT number FROM user_files WHERE tg_file_id = ?', (tg_file_id,))
    file_number = await file_number.fetchone()
    user_file_id = file_number[0] + user_id
    await cursor.execute('UPDATE user_files SET user_file_id = ? WHERE tg_file_id = ?', (user_file_id, tg_file_id))
    await connect.commit()
    await cursor.close()
    await connect.close()


async def get_user_photos(user_id):
    connect = await aiosqlite.connect('Data_Storage_DB.db')
    cursor = await connect.cursor()
    try:
        await cursor.execute('SELECT user_file_id FROM user_files WHERE user_id = ? AND file_type = ?',
                             (user_id, 'photo'))
        files = await cursor.fetchall()
        return files

    finally:
        await cursor.close()
        await connect.close()


async def get_user_docs(user_id):
    connect = await aiosqlite.connect('Data_Storage_DB.db')
    cursor = await connect.cursor()
    try:
        await cursor.execute('SELECT user_file_id FROM user_files WHERE user_id = ? AND file_type = ?',
                             (user_id, 'document'))
        files = await cursor.fetchall()
        return files

    finally:
        await cursor.close()
        await connect.close()


async def get_user_sounds(user_id):
    connect = await aiosqlite.connect('Data_Storage_DB.db')
    cursor = await connect.cursor()
    try:
        await cursor.execute(
            'SELECT user_file_id FROM user_files WHERE user_id = ? AND file_type IN (?, ?)',
            (user_id, 'audio', 'voice'))
        files = await cursor.fetchall()
        return files

    finally:
        await cursor.close()
        await connect.close()


async def get_file(user_file_id):
    connect = await aiosqlite.connect('Data_Storage_DB.db')
    cursor = await connect.cursor()
    try:
        await cursor.execute('SELECT tg_file_id FROM user_files WHERE user_file_id = ?', (user_file_id,))
        file = await cursor.fetchone()
        return file[0]
    finally:
        await cursor.close()
        await connect.close()


async def is_voice(user_file_id):
    connect = await aiosqlite.connect('Data_Storage_DB.db')
    cursor = await connect.cursor()
    try:
        await cursor.execute('SELECT file_type FROM user_files WHERE user_file_id = ?', (user_file_id,))
        file_type = await cursor.fetchone()
        if file_type == 'voice':
            return True
        return False
    finally:
        await cursor.close()
        await connect.close()


def create_pagination_kb(page: int, total_items: int, items_per_page: int) -> types.InlineKeyboardMarkup:
    kb_buttons = []

    pagination_buttons = []
    if page > 0:
        pagination_buttons.append(types.InlineKeyboardButton(text='⬅️ Назад', callback_data='prev_page'))
    pagination_buttons.append(types.InlineKeyboardButton(
        text=f"{page + 1}/{max(1, (total_items + items_per_page - 1) // items_per_page)}",
        callback_data='page_info'
    ))
    if (page + 1) * items_per_page < total_items:
        pagination_buttons.append(types.InlineKeyboardButton(text='Вперед ➡️', callback_data='next_page'))

    kb_buttons.append(pagination_buttons)

    return types.InlineKeyboardMarkup(inline_keyboard=kb_buttons)

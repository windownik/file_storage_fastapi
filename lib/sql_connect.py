import datetime
import os
import time

from fastapi_asyncpg import configure_asyncpg
from lib.app_init import app
from fastapi import Depends


password = os.environ.get("DATABASE_PASS")
host = os.environ.get("DATABASE_HOST")
port = os.environ.get("DATABASE_PORT")
db_name = os.environ.get("DATABASE_NAME")

password = 102015 if password is None else password
host = '127.0.0.1' if host is None else host
port = 5432 if port is None else port
db_name = 'file_storage' if db_name is None else db_name

# Создаем новую таблицу
data_b = configure_asyncpg(app, f'postgres://postgres:{password}@{host}:{port}/{db_name}')


# Создаем новую таблицу
# Таблица для записи статей информации о файлах
async def create_files_main_table(db):
    await db.execute(f'''CREATE TABLE IF NOT EXISTS files_main (
 id SERIAL PRIMARY KEY,
 file_name TEXT DEFAULT '0',
 file_type TEXT DEFAULT '0',
 owner_id INTEGER DEFAULT 0,
 little_file_id INTEGER DEFAULT 0,
 middle_file_id INTEGER DEFAULT 0,
 row_file_id INTEGER DEFAULT 0,
 create_date BIGINT DEFAULT 0
 )''')


# Создаем новую таблицу
# Таблица для записи статей информации о файлах
async def create_files_table(db):
    await db.execute(f'''CREATE TABLE IF NOT EXISTS files (
 id SERIAL PRIMARY KEY,
 file_path TEXT DEFAULT '0',
 file_size BIGINT DEFAULT 0,
 main_file_id INTEGER REFERENCES files(id));''')


# Обновляем информацию
async def update_data(db: Depends, table: str, name: str, id_data, data, id_name: str = 'id'):
    await db.execute(f"UPDATE {table} SET {name}=$1 WHERE {id_name}=$2;",
                     data, id_data)


# Создаем новую запись в базе данных
async def save_new_main_file(db: Depends, file_name: str, file_type: str, owner_id: int):
    now = datetime.datetime.now()
    file_id = await db.fetch(f"INSERT INTO files_main (file_name, file_type, owner_id, create_date) "
                             f"VALUES ($1, $2, $3, $4) "
                             f"ON CONFLICT DO NOTHING RETURNING *;", file_name, file_type, owner_id,
                             int(time.mktime(now.timetuple())))
    return file_id


# Создаем новую запись в базе данных
async def save_new_file(db: Depends, file_path: str, main_file_id: int, file_size: int):
    file_id = await db.fetch(f"INSERT INTO files (file_path, main_file_id, file_size) "
                             f"VALUES ($1, $2, $3) "
                             f"ON CONFLICT DO NOTHING RETURNING *;", file_path, main_file_id, file_size)
    return file_id


async def read_data(db: Depends, table: str, id_name: str, id_data, order: str = '', name: str = '*'):
    """Получаем актуальные события"""
    data = await db.fetch(f"SELECT {name} FROM {table} WHERE {id_name} = $1{order};", id_data)
    return data


# Удаляем все записи из таблицы по ключу
async def delete_where(db: Depends, table: str, id_name: str, data):
    await db.execute(f"DELETE FROM {table} WHERE {id_name} = $1", data)

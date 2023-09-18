import datetime
import os

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
async def create_files_table(db):
    await db.execute(f'''CREATE TABLE IF NOT EXISTS files (
 id SERIAL PRIMARY KEY,
 file_name TEXT DEFAULT '0',
 file_path TEXT DEFAULT '0',
 file_type TEXT DEFAULT '0',
 owner_id INTEGER DEFAULT 0,
 little_file_id INTEGER DEFAULT 0,
 middle_file_id INTEGER DEFAULT 0,
 file_size BIGINT DEFAULT 0,
 client_file_id INTEGER DEFAULT 0,
 create_date timestamptz
 )''')


# Создаем новую запись в базе данных
async def save_new_file(db: Depends, file_name: str, file_path: str, file_type: str, owner_id: int, file_size: int,
                        client_file_id: int):
    now = datetime.datetime.now()
    file_id = await db.fetch(f"INSERT INTO files (file_name, file_path, file_type, owner_id, file_size, client_file_id,"
                             f" create_date) "
                             f"VALUES ($1, $2, $3, $4, $5, $6, $7) "
                             f"ON CONFLICT DO NOTHING RETURNING *;", file_name, file_path, file_type, owner_id,
                             file_size, client_file_id, now)
    return file_id

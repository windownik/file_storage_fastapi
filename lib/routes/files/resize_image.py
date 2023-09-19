import os

from PIL import Image
from fastapi import Depends, UploadFile

from lib import sql_connect as conn


async def save_resize_img(db: Depends, file: UploadFile, file_path: str, main_file_id: int,
                          filename: str, size: int = 1):
    small_file_id = (await conn.save_new_file(db=db, file_path=file_path, file_size=0, main_file_id=main_file_id))[0][0]
    small_filename = f"{small_file_id}.{file.filename.split('.')[1]}"
    await conn.update_data(table='files', name='file_path', data=f"{file_path}{small_filename}",
                           id_data=small_file_id, db=db)
    await conn.update_data(table='files_main', name='little_file_id' if size == 1 else 'middle_file_id',
                           data=small_file_id, id_data=main_file_id, db=db)

    image = Image.open(f"{file_path}{filename}")

    width, height = image.size
    coefficient = height / 100
    new_width = (width / coefficient) * size
    try:
        resized_image = image.resize((int(new_width), 100 * size))
        resized_image.save(f"{file_path}{small_filename}")
        if os.path.exists(f"{file_path}{small_filename}"):  # Проверяем существование файла
            file_size = os.path.getsize(f"{file_path}{small_filename}")  # Получаем размер файла в байтах
            await conn.update_data(table='files', name='file_size', data=file_size,
                                   id_data=small_file_id, db=db)
        else:
            file_size = 0

    except Exception as ex:
        print(ex)
        await conn.delete_where(table='files', id_name='id', data=small_file_id, db=db)
        await conn.update_data(table='files', name='little_file_id' if size == 1 else 'middle_file_id',
                               data=0,
                               id_data=main_file_id, db=db)
        small_file_id = 0
        file_size = 0

    return small_file_id, file_size

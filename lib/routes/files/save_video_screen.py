import os

from PIL import Image
from fastapi import Depends

from lib import sql_connect as conn


async def save_video_screen(db: Depends, main_file_id: int, filename: str):
    from moviepy.editor import VideoFileClip

    screen_file_id = (await conn.save_new_file(db=db, file_path='files/img/', file_size=0,
                                               main_file_id=main_file_id))[0][0]

    small_filename = f"{screen_file_id}.jpg"
    await conn.update_data(table='files', name='file_path', data=f"files/img/{small_filename}",
                           id_data=screen_file_id, db=db)

    await conn.update_data(table='files_main', name='little_file_id', data=screen_file_id,
                           id_data=main_file_id, db=db)

    # Загрузите видео с помощью moviepy
    video = VideoFileClip(f"files/video/{filename}")
    if video.duration < 5:
        screenshot_time = 0
    else:
        screenshot_time = video.duration / 5

    # Получите кадр на определенной секунде времени
    frame = video.get_frame(screenshot_time)

    # Создайте изображение с помощью Pillow из кадра
    image = Image.fromarray(frame)
    image.save(f"files/img/{small_filename}")
    video.reader.close()
    video.audio.reader.close_proc()

    if os.path.exists(f"files/img/{small_filename}"):  # Проверяем существование файла
        file_size = os.path.getsize(f"files/img/{small_filename}")  # Получаем размер файла в байтах
        await conn.update_data(table='files', name='file_size', data=file_size, id_data=screen_file_id, db=db)
    return screen_file_id

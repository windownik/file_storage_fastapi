import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=origins,
    allow_headers=["Origin, X-Requested-With, Content-Type, Accept"],
)


# Путь к текущей директории
current_directory = os.getcwd()

# Проверка наличия папки 'files'
files_directory = os.path.join(current_directory, 'files')
if not os.path.exists(files_directory):
    # Если папки 'files' нет, создаем ее
    os.makedirs(files_directory)

# Проверка и создание папок 'docs', 'img', 'ms_doc' внутри 'files'
subdirectories = ['img', 'ms_doc', 'docs', 'video', 'audio', 'file']
for subdirectory in subdirectories:
    subdirectory_path = os.path.join(files_directory, subdirectory)
    if not os.path.exists(subdirectory_path):
        os.makedirs(subdirectory_path)

print("Folder structure has been successfully checked and created.")

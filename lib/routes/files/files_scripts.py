import os

from fastapi import Depends
from lib import sql_connect as conn

ip_server = os.environ.get("IP_SERVER")
ip_port = os.environ.get("PORT_SERVER")

ip_port = 80 if ip_port is None else ip_port
ip_server = "127.0.0.1" if ip_server is None else ip_server


async def create_file_json(file, db: Depends) -> dict:
    resp = {'ok': True,
            'file_id': file['id'],
            'file_name': file['file_name'],
            'file_type': file['file_type'],
            'creator_id': file['owner_id'],
            }

    little_id = file['little_file_id']
    middle_id = file['middle_file_id']
    try:
        middle_files_size = (await conn.read_data(db=db, table='files', id_name='id', id_data=middle_id))[0][2]
    except Exception as _ex:
        middle_files_size = 0
        print(_ex)

    try:
        row_files_size = (await conn.read_data(db=db, table='files', id_name='id', id_data=file['row_file_id']))[0][2]
    except Exception as _ex:
        row_files_size = 0
        print(_ex)

    try:
        little_files_size = (await conn.read_data(db=db, table='files', id_name='id', id_data=little_id))[0][2]
    except Exception as _ex:
        little_files_size = 0
        print(_ex)

    list_files = []

    if file['file_type'] == 'video':

        resp['file_url'] = f"http://{ip_server}:{ip_port}/download?file_id={file['row_file_id']}"
        resp['file_size'] = row_files_size

        if little_id != 0:
            resp['screen_url'] = f"http://{ip_server}:{ip_port}/download?file_id={little_id}"

    elif file['file_type'] == 'image':

        list_files.append({
            'file_size': row_files_size,
            'url': f"http://{ip_server}:{ip_port}/download?file_id={file['row_file_id']}"
        })
        if middle_id != 0:
            list_files.append({
                'file_size': middle_files_size,
                'url': f"http://{ip_server}:{ip_port}/download?file_id={middle_id}"
            })
        if little_id != 0:
            list_files.append({
                'file_size': little_files_size,
                'url': f"http://{ip_server}:{ip_port}/download?file_id={little_id}"
            })
        resp['images'] = list_files
    else:
        resp['file_url'] = f"http://{ip_server}:{ip_port}/download?file_id={file['row_file_id']}"
        resp['file_size'] = row_files_size
    return resp

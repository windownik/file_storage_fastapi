import os

import starlette.status as _status
from fastapi import Depends
from fastapi import UploadFile
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse

from lib import sql_connect as conn
from lib.response_examples import create_file_res
from lib.routes.files.files_scripts import create_file_json
from lib.routes.files.resize_image import save_resize_img
from lib.routes.files.save_video_screen import save_video_screen
from lib.sql_connect import data_b, app

ip_server = os.environ.get("IP_SERVER")
ip_port = os.environ.get("PORT_SERVER")

ip_port = 8000 if ip_port is None else ip_port
ip_server = "127.0.0.1" if ip_server is None else ip_server


@app.get(path='/download', tags=['Files'])
async def download_file(file_id: int, db=Depends(data_b.connection), ):
    """Here you download file by id"""
    file = await conn.read_data(db=db, table='files', id_name='id', id_data=file_id, name='*')
    if not file:
        return JSONResponse(status_code=_status.HTTP_400_BAD_REQUEST,
                            content={'desc': 'bad file id'})
    file_path = file[0]['file_path']
    file_name = await conn.read_data(db=db, name='file_name, file_type, little_file_id', table='files_main', id_name='id',
                                     id_data=file[0]['main_file_id'],)
    if file_name[0][1] == 'video':
        if file_id == file_name[0][2]:
            return FileResponse(path=file_path, media_type='multipart/form-data', filename='screen.jpeg')
    return FileResponse(path=file_path, media_type='multipart/form-data', filename=file_name[0][0])


@app.get(path='/file', tags=['Files'], responses=create_file_res)
async def get_file_by_file_id(file_id: int, db=Depends(data_b.connection), ):
    """Get all information about file by file_id"""
    file = await conn.read_data(db=db, table='files_main', id_name='id', id_data=file_id, name='*')
    if not file:
        return JSONResponse(status_code=_status.HTTP_400_BAD_REQUEST,
                            content={'desc': 'bad file id'})

    resp = await create_file_json(file[0], db=db)

    return JSONResponse(content=resp,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.post(path='/file_upload', tags=['Files'], responses=create_file_res)
async def upload_file(file: UploadFile, user_id: int = 0, db=Depends(data_b.connection), ):
    """
    Upload file to server\n
    file_type in response:
    .jpg and .jpeg is image,\n
    .xlsx and .doc is ms_doc,\n
    .mp4  is video,\n
    other files get type file\n
    msg_id: if file attached to message with msg_id
    """

    if (file.filename.split('.')[-1]).lower() == 'jpg' or (file.filename.split('.')[-1]).lower() == 'jpeg':
        file_path = f'files/img/'
        file_type = 'image'
    elif file.filename.split('.')[1] == 'xlsx' or file.filename.split('.')[1] == 'doc':
        file_path = f'files/ms_doc/'
        file_type = 'ms_doc'
    elif file.filename.split('.')[1] == 'txt' or file.filename.split('.')[1] == 'pdf':
        file_path = f'files/docs/'
        file_type = 'document'
    elif file.filename.split('.')[1] == 'mp4':
        file_path = f'files/video/'
        file_type = 'video'
    elif file.filename.split('.')[1] == 'mp3':
        file_path = f'files/audio/'
        file_type = 'audio'
    else:
        file_path = f'files/file/'
        file_type = 'file'
    main_file_data = await conn.save_new_main_file(db=db, file_name=file.filename, file_type=file_type,
                                                   owner_id=user_id)

    file_data = await conn.save_new_file(db=db, file_size=file.size, file_path=file_path,
                                         main_file_id=main_file_data[0]['id'])
    await conn.update_data(table='files_main', name='row_file_id', data=file_data[0][0], id_data=main_file_data[0][0],
                           db=db)
    main_file_id = main_file_data[0][0]

    filename = f"{main_file_id}.{file.filename.split('.')[1]}"
    await conn.update_data(table='files', name='file_path', data=f"{file_path}{filename}", id_data=file_data[0][0],
                           db=db)
    b = file.file.read()

    f = open(f"{file_path}{filename}", 'wb')
    f.write(b)
    f.close()
    list_files = [{
        'file_size': file.size,
        'url': f"http://{ip_server}:{ip_port}/download?file_id={file_data[0][0]}",
    }]
    resp = {'ok': True,
            'file_id': main_file_id,
            'file_name': main_file_data[0][1],
            'file_type': file_type,
            'creator_id': user_id,
            }
    if file_type == 'image':
        middle_file_id, middle_file_size = await save_resize_img(db=db, file=file, file_path=file_path,
                                                                 main_file_id=main_file_id, filename=filename, size=4)

        small_file_id, small_file_size = await save_resize_img(db=db, file=file, file_path=file_path,
                                                               main_file_id=main_file_id, filename=filename, )
        if middle_file_id != 0:
            list_files.append({
                'file_size': middle_file_size,
                'url': f"http://{ip_server}:{ip_port}/download?file_id={middle_file_id}"
            })
        if small_file_id != 0:
            list_files.append({
                'file_size': small_file_size,
                'url': f"http://{ip_server}:{ip_port}/download?file_id={small_file_id}"
            })
        resp['images'] = list_files

    elif file_type == 'video':
        screen_id = await save_video_screen(db=db, main_file_id=main_file_id, filename=filename)
        resp['file_url'] = f"http://{ip_server}:{ip_port}/download?file_id={file_data[0][0]}"
        resp['screen_url'] = f"http://{ip_server}:{ip_port}/download?file_id={screen_id}"
        resp['file_size'] = file.size

    else:
        resp['file_url'] = f"http://{ip_server}:{ip_port}/download?file_id={file_data[0][0]}"
        resp['file_size'] = file.size

    return JSONResponse(content=resp,
                        headers={'content-type': 'application/json; charset=utf-8'})

"""
Чтобы обратиться к методу API ВКонтакте, Вам необходимо выполнить POST или GET запрос такого вида:
https://api.vk.com/method/METHOD_NAME?PARAMETERS&access_token=ACCESS_TOKEN&v=V

Он состоит из нескольких частей:
METHOD_NAME (обязательно) — название метода API, к которому Вы хотите обратиться.
Обратите внимание: имя метода чувствительно к регистру.
PARAMETERS (опционально) — входные параметры соответствующего метода API, последовательность пар name=value, разделенных
амперсандом. Список параметров указан на странице с описанием метода.
ACCESS_TOKEN (обязательно) — ключ доступа.
V (обязательно) — используемая версия API. Использование этого параметра применяет некоторые изменения в формате ответа
различных методов. На текущий момент актуальная версия API — 5.131. Этот параметр следует передавать со всеми запросами.
"""
import string
from pprint import pprint
import json
import requests as requests


def file_from_vk(owner_id: string):
    TOKEN = '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008'
    url = 'https://api.vk.com/method/photos.get'
    params = {
        'owner_id': owner_id,
        'access_token': TOKEN,
        'album_id': 'profile',
        'v': '5.131',
        'extended': '1',
        'photo_sizes': '1'
    }
    photos_vk = []
    response = requests.get(url, params=params)
    if 'response' in response.json():
        print('Запрос на скачивание фото из контакта успешен')
        for items in response.json()['response']['items']:
            likes = items['likes']['count']
            print(f'Скачиваем фото {items["id"]}(Кодовое имя {likes})')
            max_width = 0
            photo = ''
            photo_size = ''
            for sizes in items['sizes']:
                if sizes['width'] > max_width:
                    max_width = sizes['width']
                    photo = sizes['url']
                    photo_size = sizes['type']
            if photo:
                photos_vk.append({'date': items['date'],
                                  'likes': likes,
                                  'photo_url': photo,
                                  'size': photo_size})
        return photos_vk
    else:
        print('Ошибка - ', response.json()['error']['error_msg'])
        return


def file_to_disk(photos_disk: list, OAuth: string):
    resource_url = "https://cloud-api.yandex.net/v1/disk/resources"
    upload_url = resource_url + '/upload'
    headers = {'Content-Type': 'application/json',
               'Authorization': 'OAuth {}'.format(OAuth)}
    response = requests.put(resource_url, headers=headers, params={'path': 'vk/'})
    if response.status_code == 201 or response.status_code == 409:
        print('ЯДиск готов принимать файлы')
        info_json = []
        for photo in photos_disk:
            name = str(photo['likes'])
            params = {'url': photo['photo_url'],
                      'path': 'vk/' + name}
            response = requests.post(upload_url, headers=headers, params=params)
            if response.status_code == 202:
                print(f'Файл {name} загружен на ЯДиск')
                info_json.append({'file_name': name,
                                  'size': photo['size']})
            else:
                print('Ошибка при загрузке фото -', response.json()['message'])
                return
    else:
        print('Ошибка при подключении к ЯДиску -', response.json()['message'])
        return
    return info_json


id_vk = input('Введите id пользователя vk')
photos = file_from_vk(id_vk)
if photos:
    token = input('Введите токен с Полигона Яндекс.Диска')
    json_ = file_to_disk(photos, token)
    if json_:
        with open("photo_from_vk.json", 'x') as json_file
            json.dump(json_, file_json, ensure_acsii = False, indent=2) 
        print('Выходной файл:')
        pprint(json_)
else:
    print('Шеф, всё пропало!')

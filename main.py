import requests
import json
from token_vk import TOKEN_VK
import time
from tqdm import tqdm
import sys


class VK_USERS:

    url_vk = 'https://api.vk.com/method/'
    url_yd = 'https://cloud-api.yandex.net/v1/disk/resources'

    URL_UPLOAD_LINK: str = "https://cloud-api.yandex.net/v1/disk/resources/upload"


    def __init__(self):
        self.version = '5.131'
        self.token_vk = TOKEN_VK
        self.vk_id = input('введите id пользователя vk: ')
        self.token_yd = input('введите токен Яндекс-Диска: ')
        self.yd_folder = input('введите название папки для загрузки фотографий: ')
        try:
            self.count_save = int(input('Введите максимальное число сохраняемых фотографий(по умолчанию 5): '))
        except ValueError:
            self.count_save = 5
        self.mistake = 0


    @property
    def header(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {self.token_yd}'
        }

    def get_response_photos_vk(self):
        photos_get_url = self.url_vk + 'photos.get'
        params = {
            'access_token': self.token_vk,
            'v': self.version,
            'owner_id': self.vk_id,
            'album_id': 'profile',
            'extended': 'likes',
            'photo_sizes': 1,
            'count': self.count_save
        }
        response = requests.get(photos_get_url, params=params)
        if response.status_code != 200:
            self.mistake = 1
            print('Failed')
        return response.json()

    def creation_json(self, info):
        with open('json_file', 'w') as f:
            json.dump(info, f, ensure_ascii=False, indent=4)

    def put_yd_folder(self):
        params = {'path': self.yd_folder}
        response = requests.put(url=self.url_yd, headers=self.header, params=params)

    def upload_folder_file_yd(self, file_name, url):
        self.put_yd_folder()
        file_path = self.yd_folder + '/' + file_name
        params = {'url': url, 'path': file_path}
        response = requests.post(url=self.URL_UPLOAD_LINK, headers=self.header, params=params)
        if response.status_code == 202:
            for number in tqdm(range(self.count_bar), total=self.count_save, desc=f"Loading photo"):
                time.sleep(0.3)
        else:
            sys.exit(f'Ошибка: Яндекс-Диск недоступен')

    def get_json_file_info_and_upload_file(self):
        count = 0
        self.count_bar = 1
        if 'error' in self.get_response_photos_vk():
            self.mistake = 1
            print(f'Ошибка: аккаунт ID:{self.vk_id} недоступен')
        elif self.get_response_photos_vk()['response'].get('count', False) == 0:
            self.mistake = 1
            print(f'В аккаунте ID:{self.vk_id} нет фотографий')
        else:
            info_json = []
            if_repeat_file_name = []
            for items in self.get_response_photos_vk()['response']['items']:
                if count < self.count_save:
                    info_dict = {'file_name': f"{str(items['likes']['count'])}" + '.jpg',
                                 'size': f"{items['sizes'][-1]['type']}"
                                 }
                    file_name = f"{str(items['likes']['count'])}" + '.jpg'
                    if file_name not in if_repeat_file_name:
                        info_json.append(info_dict)
                        if_repeat_file_name.append(file_name)
                        self.upload_folder_file_yd(file_name, f"{items['sizes'][-1]['url']}")
                        count += 1
                        self.count_bar += 1
                    else:
                        info_dict = {'file_name': f"{str(items['likes']['count'])}" + f"{str(items['date'])}" + '.jpg',
                                     'size': f"{items['sizes'][-1]['type']}"
                                     }
                        file_name = f"{str(items['likes']['count'])}" + f"({str(items['date'])})" + '.jpg'
                        info_json.append(info_dict)
                        if_repeat_file_name.append(file_name)
                        self.upload_folder_file_yd(file_name, f"{items['sizes'][-1]['url']}")
                        count += 1
                        self.count_bar += 1
            return self.creation_json(info_json)

    def start(self):
        self.get_json_file_info_and_upload_file()
        if self.mistake != 1:
            print(f'\n Фотографии на Яндекс Диск  в папку:  {self.yd_folder} успешно загружены')

if __name__ == '__main__':
    uploader = VK_USERS()
    uploader.start()

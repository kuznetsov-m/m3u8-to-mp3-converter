import vk_api
from vk_api.audio import VkAudio
import requests
import shutil
import os
import itertools
from converter_m import m3u8_to_mp3_advanced


def captcha_handler(captcha):
    """ При возникновении капчи вызывается эта функция и ей передается объект
        капчи. Через метод get_url можно получить ссылку на изображение.
        Через метод try_again можно попытаться отправить запрос с кодом капчи
    """

    f = open('image.png', 'wb')
    f.write(captcha.get_image())
    f.close()
    
    key = input("Enter captcha code {0}: ".format(captcha.get_url())).strip()

    # Пробуем снова отправить запрос с капчей
    return captcha.try_again(key)


def make_safe_filename(filename):
    keepcharacters = (' ','.','-','_','(',')',',','[',']','&','\'')
    return "".join(c for c in filename if c.isalnum() or c in keepcharacters).rstrip()[:200]

if __name__ == '__main__':
    # Authentication
    login, password = '', ''
    vk_session = vk_api.VkApi(login, password, captcha_handler=captcha_handler)

    try:
        vk_session.auth()
    except vk_api.AuthError as error_msg:
        print(error_msg)

    # Download tracks
    vkaudio = VkAudio(vk_session)
    user_id = 1
    tracks_path = 'tracks'

    if not os.path.exists(tracks_path):
        os.makedirs(tracks_path)

    track_counter = 0
    while True:
        try:
            for track in itertools.islice(vkaudio.get_iter(owner_id=user_id), track_counter, None):
                original_name = f'{track.get("artist")} - {track.get("title")}'
                safe_name = make_safe_filename(original_name)
                print(f'{"!!! " if original_name != safe_name else ""}{track_counter}. {original_name} -> {safe_name}')

                # if file exist and size > 2 Mb   -   skipping
                if os.path.exists(f'{tracks_path}/{safe_name}.mp3') and os.path.getsize(f'{tracks_path}/{safe_name}.mp3') > 2 * 1024 * 1024:
                    print('Track already downloaded. Skip.')
                else:
                    m3u8_to_mp3_advanced(f'{tracks_path}/{safe_name}', track.get('url'))
                    # remove temp x.mp3 file
                    os.remove(f'{tracks_path}/{safe_name}x.mp3')

                track_counter += 1
            break
        except Exception as e:
            print(f'Exception: {e}')
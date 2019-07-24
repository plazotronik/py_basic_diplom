#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests


URL = 'https://translate.yandex.net/api/v1.5/tr.json/translate'
KEY_API = 'trnsl.1.1.20190704T182934Z.17f33d8db55385c6.e6d41260c9ccabfba9197455fd6d6679fec9bf38'
LNG_OUT = 'RU'
LEGAL = f'\n{"=" * 67}\nПереведено сервисом «Яндекс.Переводчик» http://translate.yandex.ru/\n'


def translate(text, lang='en'):
    '''
    translation input text
    https://translate.yandex.net/api/v1.5/tr.json/translate
     ? [key=<API-ключ>]
     & [text=<переводимый текст>]
     & [lang=<направление перевода>]
     & [format=<формат текста>]
     & [options=<опции перевода>]
     & [callback=<имя callback-функции>]

    :return:
    translated text
    '''
    params = {
        'key': KEY_API,
        'text': text,
        'lang': '{}-{}'.format(lang, LNG_OUT).lower(),
    }
    response = requests.get(URL, params=params)
    return ''.join(response.json()['text'])

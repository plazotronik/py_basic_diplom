#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from translate import translate
from pprint import pprint
from time import sleep
import requests
import tqdm
import json
import os


URL = 'https://api.vk.com/method/'
VER = '5.101'
TOKEN = '73eaea320bdc0d3299faa475c196cfea1c4df9da4c6d291633f9fe8f83c08c4de2a3abf89fbc3ed8a44e1'


def make_output_dir():
    """
    check folder name "output". if no -> create.
    :return:
    """
    if 'output' not in os.listdir():
        os.mkdir('output')


def write_json(text, id, members=0, mode='wt'):
    '''
    write text to file

    :param text:
    json data
    :param id:
    int/str id`s user
    :param members:
     count member friends of group
    :param mode:
    write text default
    :return:
    file with text in folder name output
    '''
    out_file = os.path.join('output', f'groups_id-{id}_members-{members}.json')
    txt = json.dumps(text, sort_keys=True, indent=4, ensure_ascii=False)
    with open(out_file, mode=mode, encoding='utf-8-sig') as file:
        file.write(txt)


class UserVK:
    """
    This class is a user on site vk.com
    """
    def __init__(self, id='171691064'):
        """
        Создание экземпляра класса. По-дефолту eshmargunov))
        Таймаут на выполнение запроса 0.2 секунды достаточно для вхождения в ограничение 3 запроса в секунду,
        т.к. дополнительно учитывается время выполнения кода и самого запроса...

        :param id:
        user id(s)
        """
        method = 'users.get'
        parametrs = {
            'user_ids': id,
            'fields': 'domain',
            'v': VER,
            'access_token': TOKEN,
        }
        try:
            sleep(0.2)
            response = requests.get(url=f'{URL}{method}', params=parametrs)
            resp = response.json()['response'][0]
        except KeyError:
            resp = response.json()["error"]
            KE = f'\nВы ввели: {id}. Вероятно Вы ошиблись с вводом. Подробная ошибка:' \
                f'\n{" "*3}код_ошибки: {resp["error_code"]}\n{" "*3}описание: {translate(resp["error_msg"])}'
            print(KE)
        else:
            if 'deactivated' in resp.keys():
                self.delete = True
                self.close = True
                self.can_access_closed = False
            elif resp['is_closed'] & (not resp['can_access_closed']):
                self.close = True
                self.can_access_closed = False
                self.delete = False
            elif resp['is_closed'] & resp['can_access_closed']:
                self.close = True
                self.can_access_closed = True
                self.delete = False
            else:
                self.can_access_closed = True
                self.close = False
                self.delete = False
            self.user_id = resp['id']
            self.family = resp['last_name']
            self.name = resp['first_name']
            self.domain = resp['domain']
            self.fio = self.family + ' ' + self.name
            self.url = f'https://vk.com/{self.domain}'

    def getgroups(self):
        '''
        get list groups for self

        :return:
        list ids of all groups
        '''
        if self.delete:
            return print(f'{" " * 3}Невозможно найти сообщества - пользователь c id{self.user_id} '
                         f'удален или заблокирован.')
        elif self.close & (not self.can_access_closed):
            return print(f'{" " * 3}Невозможно найти сообщества - приватный профиль пользователя.')
        else:
            method = 'groups.get'
            parametrs = {
                'user_id': self.user_id,
                'v': VER,
                'access_token': TOKEN,
            }
            try:
                sleep(0.2)
                response = requests.get(url=f'{URL}{method}', params=parametrs)
                resp = response.json()['response']['items']
            except KeyError:
                resp = response.json()["error"]
                KE = f'\nПроизошла ошибка обращения к ключу. Возможно сервер вернул не то, что ожидалось.' \
                    f'\n{" "*3}код_ошибки: {resp["error_code"]}\n{" "*3}описание: {translate(resp["error_msg"])}'
                print(KE)
                return KE
            else:
                return resp

    def getspygroups(self, members=1):
        '''
        method for get spy groups

        :param members:
        count member friends of group
        :return:
        list ids of spy groups
        '''
        if self.delete:
            return print(f'{" " * 3}Невозможно найти сообщества - пользователь c id{self.user_id} '
                         f'удален или заблокирован.')
        elif self.close & (not self.can_access_closed):
            return print(f'{" " * 3}Невозможно найти сообщества - приватный профиль пользователя.')
        else:
            sleep(0.1)
            t = tqdm.tqdm(desc='Progress', total=1, unit=' parrots', leave=False)
            t.update(13)
            lst_spy_gid = []
            lst_tmp = self.getgroups()
            for group in lst_tmp:
                method = 'groups.getMembers'
                parametrs = {
                    'group_id': group,
                    'filter': 'friends',
                    'v': VER,
                    'access_token': TOKEN,
                }
                sleep(0.3)
                t.update(2)
                response = requests.get(url=f'{URL}{method}', params=parametrs)
                if response.json()['response']['count'] < members:
                    lst_spy_gid.append(group)
                    t.update(2)
            lst_spy = []
            if len(lst_spy_gid) == 0:
                print('\nТаковых групп пользователь не имеет.')
            else:
                for lst in lst_spy_gid:
                    globals()[f'grp_{lst}'] = GroupVK(lst)
                    lst_spy.append(globals()[f'grp_{lst}'].__dict__())
                    t.update(3)
                t.close()
                sleep(0.3)
                print('Колличество сообществ: ', len(lst_spy), 'шт.')
                pprint(lst_spy)
                return lst_spy

    def __str__(self):
        return f'{self.fio} - {self.url}'


class GroupVK:
    def __init__(self, id):
        """
        Создание экземпляра класса Группа.
        Таймаут на выполнение запроса 0.2 секунды достаточно для вхождения в ограничение 3 запроса в секунду,
        т.к. дополнительно учитывается время выполнения кода и самого запроса...

        :param id:
        group id
        """
        method = 'groups.getById'
        parametrs = {
            'group_id': id,
            'fields': 'members_count',
            'v': VER,
            'access_token': TOKEN,
        }
        sleep(0.2)
        response = requests.get(url=f'{URL}{method}', params=parametrs)
        resp = response.json()['response'][0]
        if 'deactivated' in resp.keys():
            self.membs = None
        else:
            self.membs = resp['members_count']
        self.name = resp['name']
        self.gid = resp['id']
        self.url = f'https://vk.com/club{self.gid}'

    def __dict__(self):
        return {
            "name": self.name,
            "gid": self.gid,
            "members_count": self.membs,
        }

    def __str__(self):
        return f'"name": {self.name}, "gid": {self.gid}, "members_count": {self.membs}, "url": {self.url}'


def input_id_user(members=1):
    '''
    input id(s) user(s) (+ members) -> print spy groups & create file with spy groups

    :param members:
    count member friends of group
    :return:
    print spy groups & create file with spy groups
    '''
    user_id = str(input('Введите id пользователя: ')).lower()
    try:
        tmp = UserVK(user_id)
        print(f"\nСообщества пользователя {tmp.fio} с id {tmp.user_id}:")
        write_json(tmp.getspygroups(members), user_id, members)
    except Exception:
        pass


def very_main():
    '''
    main function for communication people and program

    :return:
    good user experience
    '''
    print('\n\nДобро пожаловать в "Spy Games"'.upper())
    print('\n\nВам необходимо ввести цифру ниже, чтобы программа выполнила действие: '
          '\n\n   1. Вывод сообществ пользователя vk.com, где нет ни одного его друга.'
          '\n   2. Вывод сообществ пользователя vk.com, где есть его друзья не более, чем заданное число.'
          '\n   9. Вывод этой справки.'
          '\n   0. Выйти из программы.'
          '\n\n   В программе используется «Яндекс.Переводчик» http://translate.yandex.ru/')
    try:
        while True:
            prog = str(input(f'\n{"=" * 80}'
                             '\n\n  номер действия: '.upper()))
            if prog == '1':
                input_id_user()
            elif prog == '2':
                try:
                    input_id_user(int(input('Введите количество друзей пользователя в сообществах: ')))
                except ValueError:
                    print('\nВведено некорректное количество друзей. Это должно быть целое число. Попробуйте еще раз.')
            elif prog == '9':
                print('\n\nВам необходимо ввести цифру ниже, чтобы программа выполнила действие: '
                      '\n\n   1. Вывод сообществ пользователя vk.com, где нет ни одного его друга.'
                      '\n   2. Вывод сообществ пользователя vk.com, где есть его друзья не более, чем заданное число.'
                      '\n   9. Вывод этой справки.'
                      '\n   0. Выйти из программы.'
                      '\n\n   В программе используется «Яндекс.Переводчик» http://translate.yandex.ru/')
            elif prog == '0':
                print('\n   Надеемся Вам очень понравилась наша программа!',
                      '\n   Вопросы и предложения присылайте по адресу: info@it-vi.ru',
                      '\n   Досвидания!'.upper(),
                      '\n\n   В программе был использован «Яндекс.Переводчик» http://translate.yandex.ru/')
                break
            else:
                print('\nТакой функционал программы пока не подвезли)))'
                      '\nЕсть предложения? Пишите по адресу: info@it-vi.ru')
    except KeyboardInterrupt:
        print('\n\n   Надеемся Вам очень понравилась наша программа!',
              '\n   Вопросы и предложения присылайте по адресу: info@it-vi.ru',
              '\n   Досвидания!'.upper(),
              '\n\n   В программе был использован «Яндекс.Переводчик» http://translate.yandex.ru/')


if __name__ == '__main__':
    make_output_dir()
    very_main()

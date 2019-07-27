#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from translate import translate
from pprint import pprint
from time import sleep
import requests
import tqdm
import json
import os
import reg_auth

URL = 'https://api.vk.com/method/'
VER = '5.101'
TOKEN = reg_auth.gettoken() #'be427a11b7c20f57643d8c52d87e5f357ad196f90e59d5752449fa46f015104781de59787f9706b18aac2'


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


def exec_spy_groups(groups, members=1):
    '''
    get spy groups with execute

    :param groups:
    list ids all groups
    :param members:
    count member friends of group
    :return:
    list ids spy groups
    '''
    method = 'execute'
    groups_str = ",".join(str(i) for i in groups)
    code = '''
    var i = 0;
    var members = ''' + str(members) + ''';
    var gidsbefore = [''' + groups_str + '''];
    var gidsafter = [];
    while (i < gidsbefore.length) {
    var ids = gidsbefore.pop();
    var resp = API.groups.getMembers({"group_id": ids, "filter": "friends"});
    if (resp.count < members) {
    gidsafter.push(ids);
    }
    i = i + 1;
    }
    return gidsafter;
    '''
    parametrs = {
        'code': code.strip(),
        'v': VER,
        'access_token': TOKEN,
    }
    sleep(0.2)
    response = requests.get(url=f'{URL}{method}', params=parametrs)
    print(response.json())
    resp = response.json()['response']
    return resp

def exec_spy_groups_2(users):
    '''
    get spy groups with execute

    :param users:
    list ids all users
    :return:
    list ids spy groups
    '''
    method = 'execute'
    # print(len(users))
    users_str = ",".join(str(i) for i in users)
    print(users_str)
    code = '''
    var i = 0;
    var uidsbefore = [''' + users_str + '''];
    var gidsafter = [];
    while (i < 25) {
    var id = uidsbefore.pop();
    var resp = API.groups.get({"user_id": id});
    gidsafter.push(resp.items);
    i = i + 1;
    }
    return gidsafter;
    '''
    parametrs = {
        'code': code.strip(),
        'v': VER,
        'access_token': TOKEN,
    }
    sleep(0.3)
    response = requests.get(url=f'{URL}{method}', params=parametrs)
    print(response.json())
    resp = response.json()['response']
    return resp

def exec_spy_groups_3(group, offset=0):
    '''
    get spy groups with execute

    :param groups:
    list ids all groups
    :param members:
    count member friends of group
    :return:
    list ids spy groups
    '''
    method = 'execute'
    # groups_str = ",".join(str(i) for i in groups)
    code = '''
    var i = 0;
    var gid = [''' + str(group) + '''];
    var uids = [];
    var offset = ''' + str(offset) + ''';
    while (i < 25) {
    var resp = API.groups.getMembers({"group_id": gid, "offset": offset});
    uids.push(resp.items);
    offset = offset + 1000;
    i = i + 1;
    }
    return uids;
    '''
    parametrs = {
        'code': code.strip(),
        'v': VER,
        'access_token': TOKEN,
    }
    sleep(0.2)
    response = requests.get(url=f'{URL}{method}', params=parametrs)
    # print(response.json())
    resp = response.json()['response']
    return resp

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

    def getfriends(self):
        """
        Вывод всех друзей пользователя без создания из них экземпляров класса (ибо время выполнения кода - дорого).
        Возвращает список словарей.
        Таймаут на выполнение запроса 0.2 секунды достаточно для вхождения в ограничение 3 запроса в секунду,
        т.к. дополнительно учитывается время выполнения кода и самого запроса...

        :return
        list ids of all friends
        """
        if self.delete:
            return print(f'{" " * 3}Невозможно найти друзей - пользователь c id{self.user_id} '
                         f'удален или заблокирован.')
        elif self.close & (not self.can_access_closed):
            return print(f'{" " * 3}Невозможно найти друзей - приватный профиль пользователя.')
        else:
            method = 'friends.get'
            parametrs = {
                'user_id': self.user_id,
                'fields': 'nickname',
                'v': VER,
                'access_token': TOKEN,
            }
            try:
                sleep(0.2)
                # t = tqdm.tqdm(iterable=None, desc='Progress', total=1, unit=' parrots', leave=False)
                response = requests.get(url=f'{URL}{method}', params=parametrs)
                resp = response.json()['response']['items']
            except KeyError:
                resp = response.json()["error"]
                KE = f'\nПроизошла ошибка обращения к ключу. Возможно сервер вернул не то, что ожидалось.' \
                    f'\n{" "*3}код_ошибки: {resp["error_code"]}\n{" "*3}описание: {translate(resp["error_msg"])}'
                print(KE)
                return KE
            else:
                # print(f'\nДрузья пользователя {self.fio} ({self.url}):')
                # for i, rsp in enumerate(resp):
                #     t.update()
                #     print(f'{" " * 3}{i+1}) {rsp["last_name"]} {rsp["first_name"]} - https://vk.com/id{rsp["id"]}')
                return resp

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

    def getspygroups(self, members=0):
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
            # t = tqdm.tqdm(desc='Progress', total=1, unit=' parrots', leave=False)
            # t.update(13)
            lst_spy_gid = []
            lst_tmp = self.getgroups()
            num1 = len(lst_tmp) / 25
            if len(lst_tmp) <= 25:
                lst_spy_gid = exec_spy_groups(lst_tmp, members)
                # t.update(1)
            else:
                for i in range(num1.__round__() + 1):
                    lst_spy_gid.extend(exec_spy_groups(lst_tmp[:25], members))
                    del lst_tmp[:25]
                    # t.update(2)
            lst_spy = []
            if len(lst_spy_gid) == 0:
                print(f'\n{" "*3}Таковых групп пользователь не имеет.')
            else:
                for lst in lst_spy_gid:
                    globals()[f'grp_{lst}'] = GroupVK(lst)
                    lst_spy.append(globals()[f'grp_{lst}'].__dict__())
                    # t.update(3)
                # t.close()
                sleep(0.3)
                print('Колличество сообществ: ', len(lst_spy), 'шт.')
                pprint(lst_spy)
                return lst_spy

    def getspygroups_2(self, members=0):
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
            # sleep(0.1)
            t = tqdm.tqdm(desc='Progress', total=1, unit=' parrots', leave=False)
            t.update(13)
            # lst_spy_gid = []
            set_tmp = set(self.getgroups())
            print(set_tmp)
            list_friends = [i["id"].__str__() for i in self.getfriends()]
            # print(list_friends)
            # for uid in list_friends:
            #     print(f'{uid}')
            #     try:
            #         set_tmp.difference_update(set(UserVK(uid).getgroups()))
            #     except Exception as err:
            #         pass
            #     else:
            #         continue
                # t.update(3)
            # print(set_tmp)
            # for grp in set_tmp:
            #     print(GroupVK(grp).name)
                # pass
            num1 = len(list_friends) / 25
            # if len(list_friends) <= 25:
            #     set_tmp.difference_update(set(exec_spy_groups_2(list_friends)))
            #     # lst_spy_gid = exec_spy_groups(list_friends, members)
            #     t.update(1)
            # else:
            # set_groups = set()
            for i in range(num1.__round__() + 1):
                # set_tmp.difference_update(set(exec_spy_groups_2(list_friends[:25])))
                num = 0
                lst_tmp = exec_spy_groups_2(list_friends[:25])
                t.update(3)
                try:
                    while num < len(lst_tmp):
                        ids = lst_tmp.pop()
                        # print(ids)
                        # if ids != None:
                            # set_groups.update(set(ids))
                            # print(ids)
                        set_tmp -= set(ids)
                            # t.update(3)
                        num += 1
                except Exception:
                    pass
                # lst_spy_gid.extend(exec_spy_groups(lst_tmp[:25], members))
                del list_friends[:25]
                t.update(2)
            # set_tmp.difference_update(set_groups)
            t.close()
            sleep(0.1)
            print(len(set_tmp))
            print(set_tmp)

            # for grp in set_tmp:
            #     print(GroupVK(grp).url)
            # lst_spy = []
            # if len(lst_spy_gid) == 0:
            #     print(f'\n{" "*3}Таковых групп пользователь не имеет.')
            # else:
            #     for lst in lst_spy_gid:
            #         globals()[f'grp_{lst}'] = GroupVK(lst)
            #         lst_spy.append(globals()[f'grp_{lst}'].__dict__())
            #         t.update(3)
            #     t.close()
            #     sleep(0.3)
            #     print('Колличество сообществ: ', len(lst_spy), 'шт.')
            #     pprint(lst_spy)
            #     return lst_spy

    def getspygroups_3(self, members=0):
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
            # sleep(0.1)
            t = tqdm.tqdm(desc='Progress', total=1, unit=' parrots', leave=False)
            t.update(13)
            # lst_spy_gid = []
            list_guids = self.getgroups()
            # print(list_guids)
            list_spy_guids = []
            list_friends = [i["id"] for i in self.getfriends()]
            # print(list_friends)
            for guid in list_guids:
                list_members = []
                membs_c = GroupVK(guid).membs
                try:
                    num = membs_c / 25000
                except Exception:
                    continue
                    pass
                else:
                    t.update(3)
                    if num < 1:
                        num1 = 0
                        lst_tmp = exec_spy_groups_3(guid)
                        try:
                            while num1 < len(lst_tmp):
                                list_members.extend(lst_tmp.pop())
                                num1 += 1
                                t.update(3)
                        except Exception:
                            pass
                    else:
                        off = 0
                        num1 = 0
                        for i in range(num.__round__() + 1):
                            lst_tmp = exec_spy_groups_3(guid, off)
                            try:
                                while num1 < len(lst_tmp):
                                    list_members.extend(lst_tmp.pop())
                                    num1 += 1
                                    t.update(3)
                            except Exception:
                                pass
                            off += 25000
                        t.update(2)
                    # print(list_members)
                    set_tmp = set(list_friends)&set(list_members)
                    if len(set_tmp) != 0:
                        t.update(3)
                        print(set_tmp)
                        # continue
                    else:
                        list_spy_guids.append(guid)
                        print(list_spy_guids)
                        t.update(3)

            # except Exception:
            #     pass
            t.close()
            print(len(list_spy_guids))
            print(list_spy_guids)
            for grp in list_spy_guids:
                print(GroupVK(grp))


    def __and__(self, other):
        '''
        Вывод общих друзей двух пользователей и создание из них экземпляров класса.
        Возвращает словарь.
        Таймаут на выполнение запроса 0.2 секунды достаточно для вхождения в ограничение 3 запроса в секунду,
        т.к. дополнительно учитывается время выполнения кода и самого запроса...

        :param other:
        иной экземпляр класса UserVK
        :return:
        словарь общих друзей
        '''
        try:
            if self.delete:
                return print(f'\nНевозможно найти общих друзей. Пользователь c id{self.user_id} удален или заблокирован.')
            elif other.delete:
                return print(f'\nНевозможно найти общих друзей. Пользователь c id{other.user_id} удален или заблокирован.')
            else:
                method = 'friends.getMutual'
                parametrs = {
                    'source_uid': self.user_id,
                    'target_uid': other.user_id,
                    'v': VER,
                    'access_token': TOKEN,
                }
                if self == other:
                    print('\nСравнивать себя со своим псевдонимом не очень то логично...)) '
                          '\nДа и займет уйму времени на создание экземпляров класса. '
                          'Лучше воспользоваться методом .getfriends()\n'
                          'Например, iam.getfriends() или usr_0000000.getfriends()')
                else:
                    try:
                        sleep(0.2)
                        response = requests.get(url=f'{URL}{method}', params=parametrs)
                        resp = response.json()['response']
                    except KeyError:
                        resp = response.json()["error"]
                        KE = f'\nПроизошла ошибка обращения к ключу. Возможно сервер вернул не то, что ожидалось.' \
                            f'\n{" "*3}код_ошибки: {resp["error_code"]}\n{" "*3}описание: {translate(resp["error_msg"])}'
                        print(KE)
                        return KE
                    else:
                        # lst_friends = []
                        dict_friends = {}
                        print(f'\nОбщие друзья у пользователей {self.fio} и {other.fio}:')
                        for ind, rsp in enumerate(resp):
                            globals()[f'usr_{rsp}'] = UserVK(rsp)
                            dict_friends.update({f'usr_{rsp}': globals()[f'usr_{rsp}'].__str__()})
                            # lst_friends.append(globals()[f'usr_{rsp}'].__str__())
                            print(f'{" " * 3}{ind+1}) usr_{rsp}: {globals()[f"usr_{rsp}"]}')
                        return dict_friends
                        # return lst_friends
        except AttributeError:
            AtbE = f'\nВы ошиблись в написании одного из пользователей. Проверьте ввод и повторите позднее.'
            print(AtbE)
            return AtbE

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


def input_id_user(members=0):
    '''
    input id(s) user(s) (+ members) -> print spy groups & create file with spy groups

    :param members:
    count member friends of group
    :return:
    print spy groups & create file with spy groups
    '''
    user_id = str(input('Введите id пользовател(я/ей): ')).lower()
    if ',' in user_id:
        print('\nНаходим сообщества для каждого пользователя.')
        for user in list(user_id.split(',')):
            user = str(user.strip())
            try:
                tmp = UserVK(user)
                print(f"\nСообщества пользователя {tmp.fio} с id {tmp.user_id}:")
                write_json(tmp.getspygroups(members), user, members)
            except Exception:
                pass
    elif ' ' in user_id:
        print('\nНаходим сообщества для каждого пользователя.')
        for user in list(user_id.split(' ')):
            user = user.strip()
            try:
                tmp = UserVK(user)
                print(f"\nСообщества пользователя {tmp.fio} с id {tmp.user_id}:")
                write_json(tmp.getspygroups(members), user, members)
            except Exception:
                pass
    else:
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
    # make_output_dir()
    # very_main()
    tmp = UserVK('eshmargunov')#.getfriends()
    # print('=============', tmp)
    tmp.getspygroups_2()
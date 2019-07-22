#  и имя пользователя (eshmargunov) и id (171691064) - являются валидными входными данными.
# + получаем список друзей ползователя.
# + groups.getMembers с фильтром friends
# + если там есть друзья - откидываем, иначе - подходит.
            # - получаем список групп всех имеющихся пользователей. - old
            # - ищем difference множеств пользователя и его друзей (по идентификаторам групп) (difference_update ??) - old
# + выводим эти группы в виде json (файл groups.json), пример:
# [
#     {
#     “name”: “Название группы”,
#     “gid”: “идентификатор группы”,
#     “members_count”: количество_участников_сообщества
#     },
#     {
#     …
#     }
# ]
#
# TODO Требования к программе:
# + Программа не падает, если один из друзей пользователя помечен как “удалён” или “заблокирован”.
# - Показывает что не зависла: рисует точку или чёрточку на каждое обращение к api.
# + Не падает, если было слишком много обращений к API (Too many requests per second). Ограничение от ВК: не более 3х обращений к API в секунду. Могут помочь модуль time (time.sleep) и конструкция (try/except).
# - Код программы удовлетворяет PEP8.
# + Не использовать внешние библиотеки (vk, vkapi).
# TODO Дополнительные требования (не обязательны для получения диплома):
# + Использовать execute для ускорения работы.
# - Показывает прогресс: сколько осталось до конца работы (в произвольной форме: сколько обращений к API, сколько минут, сколько друзей или групп осталось обработать).
# - Восстанавливается если случился ReadTimeout.
# + Показывать в том числе группы, в которых есть общие друзья, но не более, чем N человек, где N задается в коде.
# Hint: Если у пользователя больше 1000 групп, можно ограничиться первой тысячей
# Hint: Удобно использовать множества
#
# https://vk.com/dev/users.get
# https://vk.com/dev/objects/user
# https://vk.com/dev/objects/group
# https://vk.com/dev/execute

# https://vk.com/dev/groups.isMember
# https://vk.com/dev/groups.getMembers
# https://vk.com/dev/groups.getById
# https://vk.com/dev/groups.get
# https://vk.com/dev/execute
# https://toster.ru/q/551164
# https://github.com/Deserter-io/vkListr/blob/master/main.js
# https://habr.com/ru/sandbox/84639/
# https://python.su/forum/topic/27508/
#


# progressbar
# http://dmitrym.ru/blog/all/progress-bar-na-pitone-v-konsoli/
# https://habr.com/ru/post/81532/ # python 2.....
# https://ru.stackoverflow.com/questions/697308/Как-сделать-правильно-progressbar-в-tkinter
# http://zetblog.ru/python-kak-sdelat-progress-bar-v-konsole.html
# +++ https://ru.stackoverflow.com/questions/564768/Нужна-ли-многопоточность-чтобы-показывать-прогресс-долговыполняющейся-функции
# + https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
# ??? https://github.com/tqdm/tqdm#ipython-jupyter-integration




from reg_auth import gettoken # get token from my file
import requests
from time import sleep, ctime
from pprint import pprint

# заюзать нормальную крутилку палки вместо дешманских точек по всему коду??? да. нет? да!
import threading
import itertools
import sys
import tqdm


URL = 'https://api.vk.com/method/'
VER = '5.101'
# TOKEN = '73eaea320bdc0d3299faa475c196cfea1c4df9da4c6d291633f9fe8f83c08c4de2a3abf89fbc3ed8a44e1' # from netology
# токен нетологии не подходит,т.к. нужно наличие доступа к группам. в этом токене вероятнее всего такого доступа нет

TOKEN = gettoken() # заменить на токен с доступом к группам...

# t = tqdm.tqdm(desc='Progress', total=1, unit=' parrots', mininterval=0.5, miniters=1)
# t.update(1)
# t.update(len(resp))


def exec_spy_groups(groups, members=0):
    '''
    get spy groups with execute

    :param groups:
    list ids groups

    :param members:
    input members for search groups
    :return:
    '''
    method = 'execute'
    groups_str = ",".join(str(i) for i in groups)
    # print(groups_str)
    code = '''
    var i = 0;
    var members = ''' + str(members) + ''';
    var gidsbefore = [''' + groups_str + '''];
    var gidsafter = [];
    while (i < gidsbefore.length) {
    var ids = gidsbefore.pop();
    var resp = API.groups.getMembers({"group_id": ids , "filter": "friends"});
    if ((resp.count == 0) || (resp.count < members)) {
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
    # print(response.json())
    resp = response.json()['response']
    # print(resp)
    return resp


class UserVK:
    """
    This class is a user on site vk.com
    """
    def __init__(self, id=171691064):
        """
        Создание экземпляра класса. По-дефолту eshmargunov))

        Таймаут на выполнение запроса 0.2 секунды достаточно для вхождения в ограничение 3 запроса в секунду,
        т.к. дополнительно учитывается время выполнения кода и самого запроса...
        :param id:
        """
        method = 'users.get'
        parametrs = {
            'user_ids': id,
            'v': VER,
            'access_token': TOKEN,
        }
        sleep(0.2)
        response = requests.get(url=f'{URL}{method}', params=parametrs)
        # print(response.json())
        # print('\b..', end='')
        resp = response.json()['response'][0]
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
        elif resp['can_access_closed'] & (not resp['is_closed']): # вернуться и убрать дубликат!!!!!!!!!
            self.close = False
            self.can_access_closed = True
            self.delete = False
        else:  # вернуться и убрать дубликат!!!!!!!!!
            self.can_access_closed = True
            self.close = False
            self.delete = False
        self.user_id = resp['id']
        self.family = resp['last_name']
        self.name = resp['first_name']
        self.fio = self.family + ' ' + self.name
        self.url = f'https://vk.com/id{self.user_id}'

    def getfriends(self):
        """
        Вывод всех друзей пользователя без создания из них экземпляров класса (ибо время выполнения кода - дорого).
        Возвращает список словарей.

        Таймаут на выполнение запроса 0.2 секунды достаточно для вхождения в ограничение 3 запроса в секунду,
        т.к. дополнительно учитывается время выполнения кода и самого запроса...
        :param id:
        """
        if self.delete:
            return print(f'Пользователь c id{self.user_id} удален или заблокирован.')
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
                response = requests.get(url=f'{URL}{method}', params=parametrs)
                # print(response.json())
                # print('\b..', end='')
                resp = response.json()['response']['items']
            except KeyError:
                resp = response.json()["error"]
                KE = f'\nПроизошла ошибка обращения к ключу. Возможно сервер вернул не то, что ожидалось.' \
                    f'\nerror_code = {resp["error_code"]}\nerror_msg = {resp["error_msg"]}'
                print(KE)
                return KE
            else:
                print(f'\nДрузья пользователя {self.fio} ({self.url}):')
                for i, rsp in enumerate(resp):
                    print(f'{" " * 3}{i+1}) {rsp["last_name"]} {rsp["first_name"]} - https://vk.com/id{rsp["id"]}')
                return resp

    def getgroups(self):
        '''
        get list groups for self
        :return:
        '''
        if self.delete:
            return print(f'Пользователь c id{self.user_id} удален или заблокирован.')
        elif self.close & (not self.can_access_closed):
            return print('\nprofile private')
        else:
            method = 'groups.get'
            parametrs = {
                'user_id': self.user_id,
                # 'extended': 1,
                # 'fields': 'members_count',
                'v': VER,
                'access_token': TOKEN,
            }
            try:
                sleep(0.2)
                response = requests.get(url=f'{URL}{method}', params=parametrs)
                # pprint(response.json())
                # print('\b..', end='')
                resp = response.json()['response']['items']
            except KeyError:
                resp = response.json()["error"]
                KE = f'\nПроизошла ошибка обращения к ключу. Возможно сервер вернул не то, что ожидалось.' \
                    f'\nerror_code = {resp["error_code"]}\nerror_msg = {resp["error_msg"]}'
                print(KE)
                return KE
            else:
                # lst_gid = [i['id'] for i in resp]
                # pprint(lst_gid)
                # print('\b..', end='')
                # return lst_gid
                # print(resp)
                return resp

    def getspygroups(self, membs=0):
        '''
        method for get spy groups

        :param membs:
        :return:
        '''
        if self.delete:
            return print(f'Пользователь c id{self.user_id} удален или заблокирован.')
        elif self.close & (not self.can_access_closed):
            return print('\nprofile private')
        else:
            lst_spy_gid = []
            # print(self.getgroups(), '+++')
            lst_tmp = self.getgroups()
            # pprint(self.getgroups())
            num1 = len(lst_tmp) / 25
            # print(num1)
            if len(lst_tmp) <= 25:
                lst_spy_gid = exec_spy_groups(lst_tmp, membs)
            else:
                for i in range(num1.__round__() + 1):
                    lst_spy_gid.extend(exec_spy_groups(lst_tmp[:25], membs))
                    del lst_tmp[:25]
            # print(lst_spy_gid, '000-----000')
            #
            lst_spy = []
            # pprint(lst_about_grp)
            # for lst in lst_about_grp:
            if len(lst_spy_gid) == 0:
                print('\nno this groups')
                return None
            else:
                for lst in lst_spy_gid:
                    globals()[f'grp_{lst}'] = GroupVK(lst)
                    lst_spy.append(globals()[f'grp_{lst}'].__dict__())
                    # print('\b..', end='')
                print('\n', lst_spy, '=====!!!====')
                return lst_spy

    def __and__(self, other):
        """
        Вывод общих друзей двух пользователей и создание из них экземпляров класса.
        Возвращает словарь.

        Таймаут на выполнение запроса 0.2 секунды достаточно для вхождения в ограничение 3 запроса в секунду,
        т.к. дополнительно учитывается время выполнения кода и самого запроса...
        :param id:
        """
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
                            f'\nerror_code = {resp["error_code"]}\nerror_msg = {resp["error_msg"]}'
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
        self.name = resp['name']
        self.gid = resp['id']
        self.membs = resp['members_count']
        self.url = f'https://vk.com/club{self.gid}'

    def __dict__(self):
        return {
            "name": self.name,
            "gid": self.gid,
            "members_count": self.membs,
        }

    def __str__(self):
        return f'"name": {self.name}, "gid": {self.gid}, "members_count": {self.membs}, "url": {self.url}'


# чуть позже
#
# def input_id_user(id, membs=0):
#     n = input('Input id user')
#     bla-bla-bla
#     add progressbar
#
# def very_main():
#     print('\n\nДобро пожаловать в bla-bla-bla!'.upper())
#     print('\n\nВам необходимо ввести номер действия, чтобы программа выполнила это действие: '
#           '\n\n   1. Вывод bla-bla-bla.'
#           '\n   2. Ввод bla-bla-bla.'
#           '\n   9. Вывод этой справки.'
#           '\n   0. Выйти из программы.')
#     while True:
#         prog = str(input(f'\n{"=" * 80}'
#                          '\n\n  номер действия: '.upper()))
#         if prog == '1':
#             input_id_user(id, membs)
#         elif prog == '2':
#             # function()
#             pass
#         elif prog == '9':
#             print('\n\nВам необходимо ввести номер действия, чтобы программа выполнила это действие: '
#                   '\n\n   1. Вывод bla-bla-bla.'
#                   '\n   2. Ввод bla-bla-bla.'
#                   '\n   9. Вывод этой справки.'
#                   '\n   0. Выйти из программы.')
#         elif prog == '0':
#             print('\n   Надеемся Вам очень понравилась наша программа!',
#                   '\n   Вопросы и предложения присылайте по адресу: info@it-vi.ru',
#                   '\n   Досвидания!'.upper())
#             break
#         else:
#             print('\nТакой функционал программы пока не подвезли)))'
#                   '\nЕсть предложения? Пишите по адресу: info@it-vi.ru')


if __name__ == '__main__':
    # very_main()


    # pass
    # # визуальный разделитель
    sep = f'\n\n{"=" * 20}\n'
    #
    # # == ЭКЗЕМПЛЯРЫ КЛАССА ==
    eshmargunov = UserVK()
    usr_3563036 = UserVK(3563036)
    usr_110553958 = UserVK(110553958)

    eshmargunov.getgroups()
    print(sep)
    usr_3563036.getgroups()
    usr_3563036.getfriends()
    usr_3563036.getspygroups()
    print(sep)
    usr_110553958.getgroups()
    usr_110553958.getspygroups()
    usr_110553958.getspygroups(3)
    print(sep)
    usr_110553958 & 0000000
    usr_110553958 & usr_3563036
    print(sep)
    grp_93481730 = GroupVK(93481730)
    print(grp_93481730.__dict__())
    print(grp_93481730)
    print(sep)

    print(sep, '\n', '+++')
    eshmargunov.getspygroups()
    eshmargunov.getspygroups(3)
    print(sep, '\n', '+++')
    usr_110553958.getspygroups()
    usr_110553958.getspygroups(3)

    sungur = UserVK(9380940)
    sergey = UserVK(2020911)
    usr_123 = UserVK(10554929)
    sergey.getspygroups()
    sergey.getspygroups(3)
    print(sep)
    sungur.getspygroups()
    sungur.getspygroups(3)
    print(sep)
    usr_123.getspygroups()
    usr_123.getspygroups(4)
    # t.close()
    # pprint(eshmargunov.getgroups())




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

# t = tqdm.tqdm(desc='Progress', total=1, unit=' parrots', mininterval=0.05, miniters=13)
# t = tqdm.tqdm(desc='Progress', total=1, unit=' parrots', leave=False)
# t = tqdm.tqdm(desc='Progress', total=1, unit=' parrots')
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
    def __init__(self, id='171691064'):
        """
        Создание экземпляра класса. По-дефолту eshmargunov))

        Таймаут на выполнение запроса 0.2 секунды достаточно для вхождения в ограничение 3 запроса в секунду,
        т.к. дополнительно учитывается время выполнения кода и самого запроса...
        :param id:
        """
        # t = tqdm.tqdm(desc='Progress', total=1, unit=' parrots', leave=False)
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
            # print(response.json())
            resp = response.json()['response'][0]
        except KeyError:
            resp = response.json()["error"]
            KE = f'\nПроизошла ошибка обращения к ключу. Возможно сервер вернул не то, что ожидалось.' \
                f'\nЛибо Вы ошиблись с вводом. Подробная ошибка:' \
                f'\nerror_code = {resp["error_code"]}\nerror_msg = {resp["error_msg"]}'
            print(KE)
            # return KE
        else:
            # print('\b..', end='')
            # resp = response.json()['response'][0]
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
            # t.update()
            self.user_id = resp['id']
            self.family = resp['last_name']
            self.name = resp['first_name']
            self.domain = resp['domain']
            self.fio = self.family + ' ' + self.name
            self.url = f'https://vk.com/{self.domain}'
            # t.close()

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
                t = tqdm.tqdm(iterable=None, desc='Progress', total=1, unit=' parrots', leave=False)
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
                    t.update()
                    print(f'{" " * 3}{i+1}) {rsp["last_name"]} {rsp["first_name"]} - https://vk.com/id{rsp["id"]}')
                # t.close()
                return resp

    def getgroups(self):
        '''
        get list groups for self
        :return:
        '''
        if self.delete:
            return print(f'Пользователь c id{self.user_id} удален или заблокирован.')
        elif self.close & (not self.can_access_closed):
            return print(f'\n{" " * 3}Невозможно найти сообщества - приватный профиль пользователя.')
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
            return print(f'\nПользователь c id{self.user_id} удален или заблокирован.')
        elif self.close & (not self.can_access_closed):
            return print(f'\n{" " * 3}Невозможно найти сообщества - приватный профиль пользователя.')
        else:
            t = tqdm.tqdm(desc='Progress', total=1, unit=' parrots', leave=False)
            t.update()
            lst_spy_gid = []
            # print(self.getgroups(), '+++')
            lst_tmp = self.getgroups()
            # pprint(self.getgroups())
            num1 = len(lst_tmp) / 25
            # print(num1)
            if len(lst_tmp) <= 25:
                lst_spy_gid = exec_spy_groups(lst_tmp, membs)
                t.update()
            else:
                for i in range(num1.__round__() + 1):
                    lst_spy_gid.extend(exec_spy_groups(lst_tmp[:25], membs))
                    del lst_tmp[:25]
                    t.update()
            # print(len(lst_spy_gid), '000-----000')
            #
            lst_spy = []
            # for lst in lst_about_grp:
            if len(lst_spy_gid) == 0:
                print('\nno this groups')
                # t.close()
                # return None
            else:
                for lst in lst_spy_gid:
                    # print(type(lst))
                    globals()[f'grp_{lst}'] = GroupVK(lst)
                    lst_spy.append(globals()[f'grp_{lst}'].__dict__())
                    t.update()
                    # print('\b..', end='')
                t.close()
                sleep(0.3)
                print(lst_spy)
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
        # t = tqdm.tqdm(desc='Progress', total=1, unit=' parrots', leave=False)
        method = 'groups.getById'
        parametrs = {
            'group_id': id,
            'fields': 'members_count',
            'v': VER,
            'access_token': TOKEN,
        }
        sleep(0.2)
        response = requests.get(url=f'{URL}{method}', params=parametrs)
        # print(response.json())
        resp = response.json()['response'][0]
        # t.update()
        if 'deactivated' in resp.keys():
            self.name = resp['name']
            self.gid = resp['id']
            self.membs = None
            self.url = f'https://vk.com/club{self.gid}'
        else:
            self.name = resp['name']
            self.gid = resp['id']
            self.membs = resp['members_count']
            self.url = f'https://vk.com/club{self.gid}'
            # t.close()

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
def input_id_user(membs=0):
    user_id = str(input('Введите id искомого пользователя: ')).lower()
    if ',' in user_id:
        print('\nВы задали больше одного пользователя. Находим сообщества для каждого.')
        for user in list(user_id.split(',')):
            user = str(user.strip())
            try:
                tmp = UserVK(user)
                # print(f"\nСообщества пользователя {tmp.fio} с id {tmp.user_id}:")
                # tmp.getspygroups(membs)
                globals()[f'usr_{user}'] = UserVK(user)
                print(f"\nСообщества пользователя {globals()[f'usr_{user}'].fio} с id {globals()[f'usr_{user}'].user_id}:")
                globals()[f'usr_{user}'].getspygroups(membs)
            except Exception as e:
                print(e)
            # else:
            #
            #     print(f"\nСообщества пользователя {tmp.fio} с id {tmp.user_id}:")
            #     tmp.getspygroups(membs)
    elif ' ' in user_id:
        print('\nВы задали больше одного пользователя. Находим сообщества для каждого.')
        for user in list(user_id.split(' ')):
            user = user.strip()
            try:
                tmp = UserVK(user)
                print(f"\nСообщества пользователя {tmp.fio} с id {tmp.user_id}:")
                tmp.getspygroups(membs)
                # globals()[f'usr_{user}'] = UserVK(user)
                # print(f"\nСообщества пользователя {globals()[f'usr_{user}'].fio} с id {globals()[f'usr_{user}'].user_id}:")
                # globals()[f'usr_{user}'].getspygroups(membs)
            except Exception:
                pass
    else:
        pass
    # t = tqdm.tqdm(desc='Progress', total=1, unit=' parrots')
    # global t
    # bla-bla-bla
    # add progressbar

def very_main():
    print('\n\nДобро пожаловать в "Spy Games"'.upper())
    print('\n\nВам необходимо ввести цифру ниже, чтобы программа выполнила нужное действие: '
          '\n\n   1. Вывод сообществ пользователя, где нет ни одного его друга.'
          '\n   2. Вывод сообществ пользователя, где есть заданное число его друзей.'
          '\n   9. Вывод этой справки.'
          '\n   0. Выйти из программы.')
    while True:
        prog = str(input(f'\n{"=" * 80}'
                         '\n\n  номер действия: '.upper()))
        if prog == '1':
            input_id_user()
        elif prog == '2':
            # function()
            pass
        elif prog == '9':
            print('\n\nВам необходимо ввести номер действия, чтобы программа выполнила это действие: '
                  '\n\n   1. Вывод bla-bla-bla.'
                  '\n   2. Ввод bla-bla-bla.'
                  '\n   9. Вывод этой справки.'
                  '\n   0. Выйти из программы.')
        elif prog == '0':
            print('\n   Надеемся Вам очень понравилась наша программа!',
                  '\n   Вопросы и предложения присылайте по адресу: info@it-vi.ru',
                  '\n   Досвидания!'.upper())
            # t.close()
            break
        else:
            print('\nТакой функционал программы пока не подвезли)))'
                  '\nЕсть предложения? Пишите по адресу: info@it-vi.ru')


if __name__ == '__main__':
    # very_main()


    # pass
    # # визуальный разделитель
    sep = f'\n\n{"=" * 20}\n'
    #
    # # == ЭКЗЕМПЛЯРЫ КЛАССА ==
    # eshmargunov_1 = UserVK()
    # usr_3563036 = UserVK(3563036)
    # usr_110553958 = UserVK(110553958)
    #
    # eshmargunov_1.getgroups()
    # print(sep)
    # usr_3563036.getgroups()
    # usr_3563036.getfriends()
    # usr_3563036.getspygroups()
    # print(sep)
    # usr_110553958.getgroups()
    # usr_110553958.getspygroups()
    # usr_110553958.getspygroups(3)
    # print(sep)
    # usr_110553958 & 0000000
    # usr_110553958 & usr_3563036
    # print(sep)
    # grp_93481730 = GroupVK(93481730)
    # print(grp_93481730.__dict__())
    # print(grp_93481730)
    # print(sep)
    #
    # print(sep, '\n', '+++')
    # eshmargunov_1.getspygroups()
    # eshmargunov_1.getspygroups(3)
    # print(sep, '\n', '+++')
    # usr_110553958.getspygroups()
    # usr_110553958.getspygroups(3)
    #
    # sungur = UserVK(9380940)
    # sergey = UserVK(2020911)
    # usr_123 = \
    # UserVK('10554929').getspygroups()
    # print(UserVK('10554929').fio)
    # print(usr_123.fio)
    # sergey.getspygroups()
    # sergey.getspygroups(3)
    # print(sep)
    # sungur.getspygroups()
    # sungur.getspygroups(3)
    # print(sep)
    # usr_123.getspygroups()
    # usr_123.getspygroups(4)
    # t.close()
    # pprint(eshmargunov.getgroups())

    # eshmargunov = UserVK('eshmargunov, plazotronik')
    # eshmargunov.getspygroups(7)
    # input_id_user(10)
    UserVK('3165485').getspygroups(15)

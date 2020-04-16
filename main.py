import re
import json
import requests
from pprint import pprint
from urllib.parse import urlencode


class User:

    def __init__(self):
        # self.USER_ID = 2402235
        # self.ACCESS_TOKEN = 'b9861ff1ff10f76023de695f9e5b14ec16dd0a891681b1bde71624795e89e93bb0838f2eb1bc74c627d36'
        self.users_groups_dict = {}

    def get_token_and_id(self):
        """
        Получение токена и ID пользователя.
        """
        APP_ID = 7405705
        AUTH_URL = 'https://oauth.vk.com/authorize'
        params = {
            'client_id': APP_ID,
            'display': 'page',
            'scope': 'groups,friends',
            'response_type': 'token',
            'v': 5.103
        }
        print('?'.join((AUTH_URL, urlencode(params))))
        print('Перейдите по ссылке, разрешите доступ и скопируйте полученную адресную строку в поле ввода ниже:')
        oauth_url = input()
        pattern = re.compile('access_token=(\S+)&(\S+)user_id=(\d+)')
        match = re.search(pattern, oauth_url)
        self.ACCESS_TOKEN = match[1]
        self.USER_ID = input(
            'Если хотите начать поиск пары для вас нажмите "Enter",'
            ' или введите ID или ник пользователя для которого хотите найти пару:\n'
        )
        if len(self.USER_ID) == 0:
            self.USER_ID = match[3]

    def get_params(self):
        """
        Возвращает стандартные парамерты запросов.
        """
        return {
            'access_token': self.ACCESS_TOKEN,
            'v': 5.103
        }

    def get_info_user(self):
        """
        Получает и возвращает информацию о пользователе.
        """
        params = self.get_params()
        params['user_ids'] = self.USER_ID
        params['fields'] = 'interests,movies,music,books,bdate'
        response = requests.get('https://api.vk.com/method/users.get', params)
        return response.json()['response']

    def get_groups_user(self):
        """
        Получает и возвращает группы пользователя.
        """
        params = self.get_params()
        params['user_id'] = self.USER_ID
        params['extended'] = 1
        params['fields'] = 'members_count'
        response = requests.get('https://api.vk.com/method/groups.get', params)
        return response.json()['response']['items']

    def gender_for_search(self):
        """
        Возвращает пол для поиска (пользовательский ввод).
        """
        while True:
            try:
                sex = int(input('Какого пола будем искать вам пару?\n'
                                'Женщина - введите цифру 1\n'
                                'Мужчина - введите цифру 2\n'
                                'Любой пол - введите цифру 0\n'))
                if 0 <= sex <= 2:
                    break
                else:
                    raise ValueError
            except ValueError:
                print('Вы ввели неправильное значение. Попробуйте снова:\n')
        return sex

    def age_range_for_search(self):
        """
        Возвращает диапазон возраста для поиска (пользовательский ввод).
        """
        while True:
            try:
                age_from = int(input('Введите от какого возраста искать пару: '))
                age_to = int(input('Введите до какого возраста искать пару: '))
                if age_from <= age_to:
                    break
                else:
                    raise ValueError
            except ValueError:
                print('Вы ввели неправильные значения. Попробуйте снова:\n')
        return age_from, age_to

    def city_for_search(self):
        """
        Возвращает город для поиска (пользовательский ввод).
        """
        city = input('Введите город в котором хотите найти себе пару: ')
        return city

    def users_search(self):
        """
        Поиск людей по заданным параметрам. Возвращает список из 1000 пользователей и инфу по ним.
        """
        params = self.get_params()
        params['sex'] = self.gender_for_search()
        range_age = self.age_range_for_search()
        params['age_from'] = range_age[0]
        params['age_to'] = range_age[1]
        params['hometown'] = self.city_for_search()
        params['status'] = 6
        params['count'] = 1000
        params['fields'] = 'interests,movies,music,books,bdate,common_count'
        params['has_photo'] = 1
        response = requests.get('https://api.vk.com/method/users.search', params)
        return response.json()['response']['items']

    def get_groups_users(self):
        """
        Возвращает список групп пользователей.
        """
        for user in self.users_search():
            params = self.get_params()
            params['user_id'] = user['id']
            users_groups = requests.get('https://api.vk.com/method/groups.get', params)
            while True:
                if 'response' in users_groups.json():
                    self.users_groups_dict[user['id']] = users_groups.json()['response']['items']
                    print('.')
                    break
                elif users_groups.json()['error']['error_code'] == 6:
                    params = self.get_params()
                    params['user_id'] = user['id']
                    users_groups = requests.get('https://api.vk.com/method/groups.get', params)
                    if 'response' in users_groups.json():
                        self.users_groups_dict[user['id']] = users_groups.json()['response']['items']
                        print('.')
                        break
                    elif users_groups.json()['error']['error_code'] != 6:
                        break
                else:
                    break
        return self.users_groups_dict


if __name__ == '__main__':
    user = User()
    # user.get_token_and_id()
    # print(user.get_info_user())
    # print(user.get_groups_user())
    # print(user.gender_to_search())
    # print(user.age_range_for_search())
    # print(user.city_for_search())
    # pprint(user.users_search())
    pprint(user.get_groups_users())

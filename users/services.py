import random


def generate_auth_code():
    """ Функция для генерирования кода авторизации """
    auth_code = ''.join([random.choice(list('0123456789')) for i in range(4)])
    return auth_code


def generate_invite_code():
    """ Функция для генерирования Invite кода """
    str1 = '0123456789'
    str2 = 'qwertyuiopasdfghjklzxcvbnm'
    str3 = str2.upper()
    rand_list = list(str1 + str2 + str3)
    random.shuffle(rand_list)
    invite_code = ''.join([random.choice(rand_list) for i in range(6)])
    return invite_code

#!/usr/bin/python
# -*- coding: utf8 -*-

import random
import string
import re
import types



class Marker(object):
    u"Базовый класс маркеров"
    type = None

    def __init__(self):
        self.markers = {} #словарь user_id = marker
        self.__marker_generates__ = {} #кеш со значениями нагенеренных маркеров

    def generate(self, users, **params):
        u"Генерируем маркеры для списка пользователей"
        for user in users:
            self.get_user(user)

    def generate_one(self, user):
        u"Генерируем маркер для пользователя"
        pass

    def validity(self, value):
        u"Проверка что значение может быть маркером"
        return True

    def convert_from_string(self, value):
        return value

    def get_user(self, user):
        u"Получаем маркер для определённого пользователя"
        us_id = user.id
        if not us_id in self.markers:
            self.generate_one(user)
        return self.markers[us_id]

    def set_user(self, user, value, validate=True):
        if validate:
            if not self.validity(value):
                return -1
        
        self.markers[user.id] = value
        self.__marker_generates__[value] = user.id
        return value
        

class MarkerUserParam(Marker):
    u"Маркером служит аттрибут пользователя"
    type = 'user_param'

    def __init__(self, param_name, **params):
        super(MarkerUserParam, self).__init__()
        self.param_name = param_name

    def generate_one(self, user):
        if not hasattr(user, self.param_name):
            raise "User not have attribute %s" % (self.param_name)
        m = getattr(user, param_name)
        self.markers[user.id] = m
        self.__marker_generates__[m] = user.id
        return m


class MarkerRandomInt(Marker):
    u"Маркером служит случайное число"
    type = 'random_int'

    def __init__(self, max_num=1e7, min_num=0, **params):
        super(MarkerRandomInt, self).__init__()
        self.max_num = max_num
        self.min_num = min_num

    def generate_one(self, user):
        m = None
        while m == None or m in self.__marker_generates__:
            m = random.randint(self.min_num, self.max_num-1)
        self.markers[user.id] = m
        self.__marker_generates__[m] = user.id
        return m

    def validity(self, value):
        type(value) != types.IntType
        if value < self.min_num: return False
        if value > self.max_num-1: return False
        return True

    def convert_from_string(self, value):
        return int(value)


class MarkerRandomString(Marker):
    u"Маркером служит случайное сгенерированная строка"
    type = 'random_str'

    def __init__(self, max_len=6, min_len=None, lowercase=False, digits=True, special_chars='', chars=None, **params):
        super(MarkerRandomString, self).__init__()
        self.length = 0

        if not min_len:
            min_len = max_len
        if min_len == max_len:
            self.length = max_len
        else:
            self.length = random.randint(min_len, max_len)

        if chars:
            self.tmpl_str = chars
        else:
            self.tmpl_str = '' #строка с используемыми символами
            if lowercase: self.tmpl_str += string.ascii_lowercase
            else: self.tmpl_str += string.ascii_letters
        if digits: self.tmpl_str += string.digits
        if special_chars: self.tmpl_str += special_chars
        self.tmpl_len = len(self.tmpl_str)

    def generate_one(self, user):
        m = None
        while m == None or m in self.__marker_generates__:
            m = ''.join([ self.tmpl_str[random.randint(0, self.tmpl_len-1)] for _ in xrange(self.length) ])
        self.markers[user.id] = m
        self.__marker_generates__[m] = user.id
        return m




marker_by_type = dict([ (x.type, x) for x in
            [ MarkerUserParam, MarkerRandomInt, MarkerRandomString ]
        ])

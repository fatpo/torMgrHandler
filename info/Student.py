# coding=utf-8
from info.Base import BaseInfo


class StudentInfo(BaseInfo):
    def __init__(self, _item):
        self.id = 0
        self.name = ''
        self.age = 0
        self.del_flag = 0
        self.create_time = ''
        self.update_time = ''

        if isinstance(_item, dict):
            for key, value in _item.iteritems():
                self.__dict__[key] = value

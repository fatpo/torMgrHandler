# coding=utf-8
from info.Base import BaseInfo


class ManagerInfo(BaseInfo):
    def __init__(self, _item=None):
        self.id = 0
        self.username = ''
        self.password = ''
        self.uri_lst = ''
        self.create_time = ''
        self.update_time = ''

        if isinstance(_item, dict):
            for key, value in _item.iteritems():
                if value:
                    self.__dict__[key] = value

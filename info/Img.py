# coding=utf-8
from info.Base import BaseInfo


class ImgInfo(BaseInfo):
    def __init__(self, _item):
        self.id = 0
        self.imgurl = ''
        self.thumbImgurl = ''
        self.height = 0
        self.width = 0
        self.bgcolor = 0
        self.imgtype = 'IMG_UNKNOW'
        self.IMG_POINT_x = 0
        self.IMG_POINT_y = 0
        self.suffix = ''
        self.type = ''
        self.key = ''
        self.del_flag = 0
        self.create_time = ''
        self.update_time = ''

        if isinstance(_item, dict):
            for key, value in _item.iteritems():
                if value:
                    self.__dict__[key] = value

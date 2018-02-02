# coding=utf-8

from Base import BaseDao
from info import Img


class ImgDao(BaseDao):
    DataInfo = Img
    table_name = 'img'  # 数据库表名
    escape_list = ['imgurl', 'thumbImgurl']  # 需要转义的list
    quot_list = ['imgtype', 'suffix', 'type', 'key', 'create_time', 'update_time']  # 需要带引号的list
    not_append_list = ['height', 'width', 'bgcolor', 'IMG_POINT_x', 'IMG_POINT_y',
                       'del_flag']  # int list，但是不可能有append操作的list，如 img_id
    append_list = []  # int list, 但是可能有append操作的list，如add_cnt, view_cnt

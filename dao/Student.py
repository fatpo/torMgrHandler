# coding=utf-8

from Base import BaseDao
from info.Student import StudentInfo


class StudentDao(BaseDao):
    DataInfo = StudentInfo
    table_name = 'student'  # table name
    escape_list = ['name']  # the list need to be escaped
    quot_list = ['create_time', 'update_time']  # the list requires quoted
    not_append_list = ['del_flag']  # int list like: img_id
    append_list = ['age']  # int list, but sometimes need to += n, like: add_cnt = add_cnt+10, view_cnt=view_cnt+1

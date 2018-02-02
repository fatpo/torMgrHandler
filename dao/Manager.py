# coding=utf-8

from dao.Base import BaseDao
from info import Manager


class ManagerDao(BaseDao):
    DataInfo = Manager
    table_name = 'Manager'  # 数据库表名
    escape_list = ['username', 'password']  # 需要转义的list
    quot_list = ['uri_lst', 'create_time', 'update_time']  # 需要带引号的list
    not_append_list = ['del_flag']  # int list，但是不可能有append操作的list，如 img_id
    append_list = []  # int list, 但是可能有append操作的list，如add_cnt, view_cnt

    @classmethod
    def get_user_sync(cls, context, conn, username):
        """
        根据username获取管理用户的同步方法
        :param context:上下文
        :param conn:数据库连接
        :return: 返回一个BaseUserInfo 或 None
        """
        sql = "select * from Manager where username='%s'" % username
        r = conn.execute(sql)
        user_item = r.fetchone()
        if user_item:
            dic = {'id': user_item[0],
                   'username': user_item[1],
                   'password': user_item[2],
                   'uri_lst': user_item[3]}
            user_info = Manager(dic)
            return user_info
        else:
            return None

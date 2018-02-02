# coding=utf-8
import logging

import tornado.gen


class BaseDao(object):
    DataInfo = None
    table_name = ''  # 数据库表名
    escape_list = []  # 需要转义的list
    quot_list = []  # 需要带引号的list
    not_append_list = []  # int list，但是不可能有append操作的list，如 img_id
    append_list = []  # int list, 但是可能有append操作的list，如add_cnt, view_cnt

    @classmethod
    @tornado.gen.coroutine
    def update(cls, context, conn, dic, where_col='id', where_col_str=False):
        """
        更新Something...
        :param context:上下文
        :param conn: 数据库连接
        :param dic: 字典
        :return:
        """
        try:
            # 如果真的不小心传了info进来，就转成dic...
            if cls.DataInfo and isinstance(dic, cls.DataInfo):
                dic = dic.to_dict()

            # 如果不带id这属性，则是耍流氓~
            assert where_col in dic

            sql = 'update %s set ' % cls.table_name
            for key, value in dic.items():
                logging.info("%s=%s" % (key, value))
                if key == where_col:
                    continue

                # 转义
                if key in cls.escape_list:
                    value = conn.escape(value)
                    sql += '`%s`=%s,' % (key, value)

                # 普通带引号
                elif key in cls.quot_list:
                    if not value:  # 把None变成''
                        value = ''
                    sql += " `%s` = '%s'," % (key, value)

                # 没有append操作的int
                elif key in cls.not_append_list:
                    sql += " `%s` = %s," % (key, value)

                # 有可能有append操作的list
                elif key in cls.append_list:
                    if isinstance(value, tuple):
                        # 匹配value=元组的情况
                        # value = (1, False)
                        # value = (1, True)
                        if value[1]:
                            sql += ' `%s` = `%s` + %s,' % (key, key, value[0])
                        else:
                            sql += ' `%s` = %s,' % (key, value[0])
                    else:
                        # 匹配value=数值的情况
                        # value = 1
                        sql += ' `%s` = %s,' % (key, value[0])

            sql = sql[0:-1]  # 去掉最后一个逗号

            where_value = dic[where_col]
            if where_col_str:
                sql += " where %s = '%s'" % (where_col, where_value)
            else:
                sql += ' where %s = %s' % (where_col, where_value)
            logging.info(sql)
            with conn.cursor() as cursor:
                yield cursor.execute(sql)
        except Exception, ex:
            logging.info("table_name=%s" % cls.table_name)
            logging.info("escape_list=%s" % cls.escape_list)
            logging.info("quot_list=%s" % cls.quot_list)
            logging.info("not_append_list=%s" % cls.not_append_list)
            logging.info("append_list=%s" % cls.append_list)
            raise ex

    @classmethod
    @tornado.gen.coroutine
    def update_by_cols(cls, context, conn, dic, where_lst):
        """
        更新Something...
        :param context:上下文
        :param conn: 数据库连接
        :param dic: 字典
        :param where_lst: where 参数列表
        :return:
        """
        try:
            assert len(where_lst) >= 1

            # 如果真的不小心传了info进来，就转成dic...
            if cls.DataInfo and isinstance(dic, cls.DataInfo):
                dic = dic.to_dict()

            sql = 'update %s set ' % cls.table_name
            for key, value in dic.items():
                logging.info("%s=%s" % (key, value))

                # 转义
                if key in cls.escape_list:
                    value = conn.escape(value)
                    sql += '`%s`=%s,' % (key, value)

                # 普通带引号
                elif key in cls.quot_list:
                    if not value:  # 把None变成''
                        value = ''
                    sql += " `%s` = '%s'," % (key, value)

                # 没有append操作的int
                elif key in cls.not_append_list:
                    sql += " `%s` = %s," % (key, value)

                # 有可能有append操作的list
                elif key in cls.append_list:
                    if isinstance(value, tuple):
                        # 匹配value=元组的情况
                        # value = (1, False)
                        # value = (1, True)
                        if value[1]:
                            sql += ' `%s` = `%s` + %s,' % (key, key, value[0])
                        else:
                            sql += ' `%s` = %s,' % (key, value[0])
                    else:
                        # 匹配value=数值的情况
                        # value = 1
                        sql += ' `%s` = %s,' % (key, value[0])

            sql = sql[0:-1]  # 去掉最后一个逗号

            where_str = " where "
            for dic in where_lst:
                key = dic['key']
                where_col = dic['where_col']
                col_str = dic['col_str']
                if col_str:
                    where_str += " %s = '%s' and" % (where_col, key)
                else:
                    where_str += " %s = %s and" % (where_col, key)
            where_str = where_str[0:-3]  # 去掉最后的and
            sql += where_str
            logging.info(sql)
            with conn.cursor() as cursor:
                yield cursor.execute(sql)
        except Exception, ex:
            logging.info("table_name=%s" % cls.table_name)
            logging.info("escape_list=%s" % cls.escape_list)
            logging.info("quot_list=%s" % cls.quot_list)
            logging.info("not_append_list=%s" % cls.not_append_list)
            logging.info("append_list=%s" % cls.append_list)
            raise ex

    @classmethod
    @tornado.gen.coroutine
    def insert(cls, context, conn, _dic):
        """
        插入Something...
        :param context:
        :param conn:
        :param _dic: 新增的字典
        :return:
        """

        try:
            # 如果真的不小心传了info进来，就转成dic...
            if cls.DataInfo and isinstance(_dic, cls.DataInfo):
                _dic = _dic.to_dict()

            sql = "insert into  %s( " % cls.table_name

            for key, value in _dic.items():
                if key in (cls.escape_list + cls.quot_list + cls.not_append_list + cls.append_list):
                    sql += "`%s`," % key
            sql = sql[0:-1]  # 去掉最后一个逗号
            sql += ") values("
            for key, value in _dic.items():

                if key in cls.escape_list:
                    value = conn.escape(value)
                    sql += "%s," % value
                elif key in cls.quot_list:
                    sql += "'%s'," % value
                elif key in cls.not_append_list:
                    sql += '%s,' % value
                elif key in cls.append_list:
                    sql += '%s,' % value
            sql = sql[0:-1]  # 去掉最后一个逗号
            sql += ') '

            logging.info("insert===> %s" % sql)

            with conn.cursor() as cursor:
                yield cursor.execute(sql)
                logging.info("insert===>cursor.lastrowid=%s" % cursor.lastrowid)
                raise tornado.gen.Return(cursor.lastrowid)
        except tornado.gen.Return:
            raise
        except Exception, ex:
            logging.info("table_name=%s" % cls.table_name)
            logging.info("escape_list=%s" % cls.escape_list)
            logging.info("quot_list=%s" % cls.quot_list)
            logging.info("not_append_list=%s" % cls.not_append_list)
            logging.info("append_list=%s" % cls.append_list)
            raise ex

    @classmethod
    @tornado.gen.coroutine
    def new(cls, context, conn, _dic):
        lastrowid = yield cls.insert(context, conn, _dic)
        raise tornado.gen.Return(lastrowid)

    @classmethod
    @tornado.gen.coroutine
    def delete(cls, context, conn, obj_id):
        """
        删除Something...
        :param context: 上下文环境
        :param conn: 数据库连接
        :param obj_id: obj id
        :return:
        """
        with conn.cursor() as cursor:
            sql = "update %s set del_flag=1 where id=%s" % (cls.table_name, obj_id)
            logging.info("DELETE = %s" % sql)
            yield cursor.execute(sql)

    @classmethod
    @tornado.gen.coroutine
    def get_by_userid_type(cls, context, conn, user_id, type, page=0, limit=10):
        """
        根据user_id + type来获取某些东西...
        :param context:
        :param conn:
        :param user_id: user_id
        :return:
        """
        with conn.cursor() as cursor:
            if page == 0:
                sql = "select * from %s where user_id=%s and `type`=%s and del_flag=0" % (
                    cls.table_name, user_id, type)
            else:
                page = page if page else 1
                start = (page - 1) * limit

                sql = "select * from %s where user_id=%s and `type`=%s and del_flag=0 limit %s offset %s " % (
                    cls.table_name, user_id, type, limit, start)
            logging.info(sql)
            yield cursor.execute(sql)
            items = cursor.fetchall()
            infos = []
            for item in items:
                info = cls.DataInfo(item)
                infos.append(info)
            raise tornado.gen.Return(infos)

    @classmethod
    @tornado.gen.coroutine
    def get_by_userid(cls, context, conn, user_id, page=0, limit=10, orderby_col="", is_desc=False, is_fetchone=False):
        """
        根据user_id 来获取某些东西...
        :param context:
        :param conn:
        :param user_id: user_id
        :return:
        """
        with conn.cursor() as cursor:
            if page == 0:
                if orderby_col:
                    if is_desc:
                        sql = "select * from %s where user_id=%s and del_flag=0 order by `%s` desc" % (
                            cls.table_name, user_id, orderby_col)
                    else:
                        sql = "select * from %s where user_id=%s and del_flag=0 order by `%s` " % (
                            cls.table_name, user_id, orderby_col)
                else:
                    sql = "select * from %s where user_id=%s and del_flag=0" % (
                        cls.table_name, user_id)
            else:
                page = page if page else 1
                start = (page - 1) * limit

                if orderby_col:
                    if is_desc:
                        sql = "select * from %s where user_id=%s and del_flag=0 order by `%s` desc limit %s offset %s " % (
                            cls.table_name, user_id, orderby_col, limit, start)
                    else:
                        sql = "select * from %s where user_id=%s and del_flag=0 order by `%s` limit %s offset %s " % (
                            cls.table_name, user_id, orderby_col, limit, start)
                else:
                    sql = "select * from %s where user_id=%s and del_flag=0 limit %s offset %s " % (
                        cls.table_name, user_id, limit, start)

            logging.info(sql)
            yield cursor.execute(sql)

            if is_fetchone:
                item = cursor.fetchone()
                if not item:
                    raise tornado.gen.Return(None)
                info = cls.DataInfo(item)
                raise tornado.gen.Return(info)
            else:
                items = cursor.fetchall()
                infos = []
                for item in items:
                    info = cls.DataInfo(item)
                    infos.append(info)
                raise tornado.gen.Return(infos)

    @classmethod
    @tornado.gen.coroutine
    def get_by_id(cls, context, conn, obj_id):
        """
        根据obj_id 来获取某些东西...
        :param context:
        :param conn:
        :param obj_id: obj_id
        :return:
        """
        with conn.cursor() as cursor:
            sql = "select * from %s where id=%s and del_flag=0" % (cls.table_name, obj_id)
            yield cursor.execute(sql)
            item = cursor.fetchone()
            info = cls.DataInfo(item)
            raise tornado.gen.Return(info)

    @classmethod
    @tornado.gen.coroutine
    def get_all(cls, context, conn, page=0, limit=10, orderby_col="", is_desc=False):
        """
        获取全部row
        :param context:
        :param conn:
        :param page:
        :param limit:
        :param orderby_col:
        :param is_desc:
        :return:
        """
        with conn.cursor() as cursor:
            if page == 0:
                if orderby_col:
                    if is_desc:
                        sql = "select * from %s where del_flag=0 order by `%s` desc" % (
                            cls.table_name, orderby_col)
                    else:
                        sql = "select * from %s where del_flag=0 order by `%s` " % (
                            cls.table_name, orderby_col)
                else:
                    sql = "select * from %s where del_flag=0" % (
                        cls.table_name)
            else:
                page = page if page else 1
                start = (page - 1) * limit

                if orderby_col:
                    if is_desc:
                        sql = "select * from %s where del_flag=0 order by `%s` desc limit %s offset %s " % (
                            cls.table_name, orderby_col, limit, start)
                    else:
                        sql = "select * from %s where del_flag=0 order by `%s` limit %s offset %s " % (
                            cls.table_name, orderby_col, limit, start)
                else:
                    sql = "select * from %s where del_flag=0 limit %s offset %s " % (
                        cls.table_name, limit, start)

            logging.info(sql)
            yield cursor.execute(sql)
            items = cursor.fetchall()
            infos = []
            for item in items:
                info = cls.DataInfo(item)
                infos.append(info)
            raise tornado.gen.Return(infos)

    @classmethod
    @tornado.gen.coroutine
    def get_by_col(cls, context, conn, key, where_col, col_str=False, is_fetchone=True, page=0, limit=10,
                   orderby_col="", is_desc=False, with_del=False, equal_lt_gt="="):
        """
        根据obj_id 来获取某些东西...
        :param where_col: 哪一列
        :param col_str: 是否需要引号包裹
        :return:
        """
        with conn.cursor() as cursor:
            _key_str = "'%s'" % key if col_str else "%s" % key
            _desc_str = " desc " if is_desc else " "
            _orderby_col_str = " order by `%s` %s" % (orderby_col, _desc_str) if orderby_col else " "
            _page_limit_str = "limit %s offset %s" % (limit, (page - 1) * limit) if page > 0 else " "
            _del_str = " " if with_del else " and del_flag=0 "

            sql = "select * from %s where `%s` %s %s %s %s %s" % (
                cls.table_name, where_col, equal_lt_gt, _key_str, _del_str, _orderby_col_str, _page_limit_str)

            logging.info(sql)
            yield cursor.execute(sql)

            if is_fetchone:
                item = cursor.fetchone()
                if not item:
                    raise tornado.gen.Return(None)
                info = cls.DataInfo(item)
                raise tornado.gen.Return(info)
            else:
                items = cursor.fetchall()
                infos = []
                for item in items:
                    info = cls.DataInfo(item)
                    infos.append(info)
                raise tornado.gen.Return(infos)

    @classmethod
    @tornado.gen.coroutine
    def get_by_cols(cls, context, conn, where_lst, is_fetchone=True, with_del=False, page=0, limit=10,
                    orderby_col="", is_desc=False):
        """
        根据某n列来获取某些东西...不管是不是del
        :param where_lst: 每个item={
                'key': key,
                'where_col': where_col, # 哪一列
                'col_str': col_str,    # col_str: 是否需要引号包裹
                'equal_lt_gt': "=",  #可供选择： =、 >=、 <=、 <、 >
        }
        :param
        :return:
        """
        with conn.cursor() as cursor:
            assert len(where_lst) >= 1

            _desc_str = " desc " if is_desc else " "
            _orderby_col_str = " order by `%s` %s" % (orderby_col, _desc_str) if orderby_col else " "
            _page_limit_str = "limit %s offset %s" % (limit, (page - 1) * limit) if page > 0 else " "
            _del_str = " " if with_del else " and del_flag=0 "

            sql = "select * from %s where " % cls.table_name

            for dic in where_lst:
                key = dic['key']
                where_col = dic['where_col']
                col_str = dic['col_str']

                equal_str = "=" if "equal_lt_gt" not in dic else dic['equal_lt_gt']
                _key_str = "'%s'" % key if col_str else "%s" % key

                sql += " `%s` %s %s and" % (where_col, equal_str, _key_str)

            # 去掉最后的and
            if where_lst:
                sql = sql[0:-3]

            sql += " %s %s %s" % (_del_str, _orderby_col_str, _page_limit_str)

            logging.info(sql)
            yield cursor.execute(sql)

            if is_fetchone:
                item = cursor.fetchone()
                if not item:
                    raise tornado.gen.Return(None)
                info = cls.DataInfo(item)
                raise tornado.gen.Return(info)
            else:
                items = cursor.fetchall()
                infos = []
                for item in items:
                    info = cls.DataInfo(item)
                    infos.append(info)
                raise tornado.gen.Return(infos)

    @classmethod
    @tornado.gen.coroutine
    def get_all_len(cls, context, conn):
        """
        获取表的row count...
        :param context:
        :param conn:
        :return:
        """
        with conn.cursor() as cursor:
            sql = "select count(1) from %s where del_flag=0" % cls.table_name
            yield cursor.execute(sql)
            item = cursor.fetchone()
            raise tornado.gen.Return(item['count(1)'])

    @classmethod
    @tornado.gen.coroutine
    def get_len_by_cols(cls, context, conn, where_lst, with_del=False):
        """
        获取表的row count...符合某些条件
        :param context:
        :param conn:
        :return:
        """
        with conn.cursor() as cursor:
            assert len(where_lst) >= 1

            _del_str = " " if with_del else " and del_flag=0 "
            sql = "select count(1) from %s where " % cls.table_name
            for dic in where_lst:
                key = dic['key']
                where_col = dic['where_col']
                col_str = dic['col_str']

                equal_str = "=" if "equal_lt_gt" not in dic else dic['equal_lt_gt']
                _key_str = "'%s'" % key if col_str else "%s" % key

                sql += " `%s` %s %s and" % (where_col, equal_str, _key_str)
            sql = sql[0:-3]
            sql += _del_str

            logging.info(sql)

            yield cursor.execute(sql)
            item = cursor.fetchone()
            raise tornado.gen.Return(item['count(1)'])

    @classmethod
    @tornado.gen.coroutine
    def search_by_col(cls, context, conn, key, col):
        """
        搜索by某一列
        :param context:
        :param conn:
        :param key:
        :param col:
        :return:
        """
        with conn.cursor() as cursor:
            sql = "select * from " + cls.table_name + " where `" + col + "` like '%" + key + "%' and del_flag=0"
            logging.info("sql = %s" % sql)

            yield cursor.execute(sql)

            infos = []
            items = cursor.fetchall()
            for item in items:
                info = cls.DataInfo(item)
                infos.append(info)

            raise tornado.gen.Return(infos)

    @classmethod
    @tornado.gen.coroutine
    def get_list_by_col(cls, context, conn, key, where_col, col_str=False, page=0, limit=10, orderby_col="",
                        is_desc=False):
        """
        根据obj_id 来获取某些东西...
        :param where_col: 哪一列
        :param col_str: 是否需要引号包裹
        :return:
        """
        with conn.cursor() as cursor:
            if orderby_col:
                if col_str:
                    if is_desc:
                        sql = "select * from %s where `%s`='%s' and del_flag=0 order by `%s` desc " % (
                            cls.table_name, where_col, key, orderby_col)
                    else:
                        sql = "select * from %s where `%s`='%s' and del_flag=0 order by `%s` " % (
                            cls.table_name, where_col, key, orderby_col)
                else:
                    if is_desc:
                        sql = "select * from %s where `%s`=%s and del_flag=0 order by `%s` desc " % (
                            cls.table_name, where_col, key, orderby_col)
                    else:
                        sql = "select * from %s where `%s`=%s and del_flag=0 order by `%s` " % (
                            cls.table_name, where_col, key, orderby_col)
            else:
                if col_str:
                    sql = "select * from %s where `%s`='%s' and del_flag=0 " % (
                        cls.table_name, where_col, key, orderby_col)
                else:
                    sql = "select * from %s where `%s`=%s and del_flag=0 " % (
                        cls.table_name, where_col, key, orderby_col)
            if page > 0:
                start = (page - 1) * limit
                sql += " limit %s offset %s " % (limit, start)

            logging.info(sql)
            yield cursor.execute(sql)
            items = cursor.fetchall()
            infos = []
            for item in items:
                info = cls.DataInfo(item)
                infos.append(info)
            raise tornado.gen.Return(infos)

    @classmethod
    @tornado.gen.coroutine
    def delete_by_col(cls, context, conn, obj_id, where_col, col_str=False):
        """
        删除Something...
        :param context: 上下文环境
        :param conn: 数据库连接
        :param obj_id: 某一个id
        :param where_col: 某一列
        :return:
        """
        with conn.cursor() as cursor:
            if col_str:
                sql = "update %s set del_flag=1 where `%s`='%s'" % (cls.table_name, where_col, obj_id)
            else:
                sql = "update %s set del_flag=1 where `%s`=%s" % (cls.table_name, where_col, obj_id)
            logging.info("DELETE = %s" % sql)
            yield cursor.execute(sql)

    @classmethod
    @tornado.gen.coroutine
    def delete_by_cols(cls, context, conn, where_lst):
        """
        删除Something...通过n个列
        :param context: 上下文环境
        :param conn: 数据库连接
        :param where_lst: where 的list
        :return:
        """
        with conn.cursor() as cursor:
            assert len(where_lst) >= 1

            sql = "update %s set del_flag=1 where " % cls.table_name
            for dic in where_lst:
                key = dic['key']
                where_col = dic['where_col']
                col_str = dic['col_str']
                if col_str:
                    sql += " `%s`= '%s' and" % (where_col, key)
                else:
                    sql += " `%s`= %s and" % (where_col, key)
            sql = sql[0:-3]  # 去掉最后的and

            logging.info("DELETE = %s" % sql)
            yield cursor.execute(sql)

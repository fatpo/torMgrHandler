# coding=utf-8
import json
import logging

import tornado.gen
import tornado.web

from dao.Image import ImgDao
from dao.Manager import ManagerDao
from mydb.db import app_pool, app_engine
from tools.MyJson import MyJsonEncoder


class H5BaseHandler(tornado.web.RequestHandler):
    DataDao = None
    HtmlPath = ""
    post_filter_key_lst = []  # post方法中屏蔽的key列表
    put_filter_key_lst = []  # get方法中屏蔽的key列表

    get_select_key_lst = []  # get方法中，过滤参数列表如：
    """
        get_select_key_lst = [{
            'key': 1,
            'where_col': 'type',
            'col_str': False,
        ]}
    """
    get_search_col_lst = []  # get方法中的搜索列
    """
        get_search_col_lst = [
            {
                'col': 'user_id',
                'method': "=",
                'col_str': False,
            },
            {
                'col': 'gongxiu_id',
                'method': "=",
                'col_str': False,
            },
            {
                'col': 'msg',
                'method': "like"
            }
        ]  # get方法中的搜索列，每一列可以指定要相等还是要like
    """

    def prepare(self):
        self.pools = [app_pool]

    def on_finish(self):
        pass

    def get_current_user(self):
        """
        解决管理后台授权问题...
        :return:
        """
        current_uri = self.request.uri.split('?')[0]
        username = self.get_secure_cookie("user")

        # 为什么这里必须用sqlalchemy，因为要同步。。。
        # 不过只是授权的check，不会怎么影响性能...
        with app_engine.connect() as conn:
            user = ManagerDao.get_user_sync(None, conn, username)
            if not user:
                logging.info("用户=%s, 不存在..." % username)
                return None

        # 如果uri_lst==ADMIN，说明这货是超级管理员，直接放行
        if user.uri_lst == 'ADMIN':
            return self.get_secure_cookie("user")

        # 如果uri_lst = '/backend/img|/backend/student'
        # 先切分成lst = ['backend/img', '/backend/student']
        # 再判断当前uri是否在lst中，若是则放行...
        for uri in user.uri_lst.split('|'):
            if current_uri in uri:
                return self.get_secure_cookie("user")

        return None

    def options(self):
        self.finish("ok")

    def write(self, chunk):
        """
        解决跨域问题

        http://www.tuicool.com/articles/7FVnMz
        在某域名下使用Ajax向另一个域名下的页面请求数据，会遇到跨域问题。
        另一个域名必须在response中添加 Access-Control-Allow-Origin 的header，才能让前者成功拿到数据。

        :param chunk:
        :return:
        """
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers', 'access_token')
        super(H5BaseHandler, self).write(chunk)

    @tornado.gen.coroutine
    @tornado.web.authenticated
    def get(self):
        """
        如果没带cmd，则是渲染html，带了cmd=get，则是获取 list
        :return:
        """
        cmd = self.get_argument('cmd', '')
        page = int(self.get_argument('page', 0))
        key = self.get_argument('key', '')
        logging.info("cmd=%s, page=%s, key=%s" % (cmd, page, key))

        if not cmd:
            self.render(self.HtmlPath)
        else:
            self.set_header("Content-Type", "application/json; charset=UTF-8")

            pool = self.pools[0]
            with (yield pool.Connection()) as conn:
                yield conn.commit()

                if key:
                    # 如果不指定列，那么就默认拿name这一列
                    if not self.get_search_col_lst:
                        infos = yield self.DataDao.search_by_col(None, conn, key, col="name")

                    # 如果指定，就遍历指定的列
                    else:
                        infos = []
                        for col_dic in self.get_search_col_lst:
                            logging.info("搜索列：%s，方法：%s" % (col_dic['col'], col_dic['method']))

                            # 如果方法是相等，则不走模糊查询，精确查找
                            # 如果方法是like，则模糊查询
                            if col_dic['method'] == 'like':
                                col_infos = yield self.DataDao.search_by_col(None, conn, key, col=col_dic['col'])
                            else:
                                # 如果列不是字符串列，那么应该只对数字敏感，其他的类型跳过
                                # 比如user_id这一列，理论是int，搜索key如果传了个字符串"广东"，我连查都不查了。。
                                if not col_dic['col_str'] and not key.isdigit():
                                    continue

                                col_infos = yield self.DataDao.get_by_col(None, conn, key=key,
                                                                          where_col=col_dic['col'],
                                                                          col_str=col_dic['col_str'], is_fetchone=False)
                            # 合并infos 和 col_infos的数据，去掉重复。
                            infos = self.get_helper_merge_data(infos, col_infos)

                    all_len = len(infos)

                    # 切割数据，手动分页
                    if page >= 1:
                        limit = 10
                        start = (page - 1) * limit
                        infos = infos[start: start + limit]
                        logging.info("手动分割数据，分页start=%s， limit=%s" % (start, limit))

                else:
                    # 管理模块获取数据带过滤条件
                    # 因为只考虑大众情况
                    if self.get_select_key_lst:
                        if hasattr(self.DataDao.DataInfo({}), 'sort_id'):
                            orderby_col = 'sort_id'
                        else:
                            orderby_col = 'id'

                        infos = yield self.DataDao.get_by_cols(None, conn, where_lst=self.get_select_key_lst,
                                                               orderby_col=orderby_col, is_desc=True, is_fetchone=False,
                                                               page=page)
                        all_len = yield self.DataDao.get_len_by_cols(None, conn, where_lst=self.get_select_key_lst)

                    # 管理模块获取全部数据
                    else:
                        # 如果info里面有sort_id属性，我们按照此属性排序, 越大越靠前
                        if hasattr(self.DataDao.DataInfo({}), 'sort_id'):
                            infos = yield self.DataDao.get_all(None, conn, page, orderby_col='sort_id', is_desc=True)
                        # 否则默认按照id排序，越大越靠前
                        else:
                            infos = yield self.DataDao.get_all(None, conn, page, orderby_col='id', is_desc=True)

                        all_len = yield self.DataDao.get_all_len(None, conn)
                logging.info("len=%s" % len(infos))

                # infos -> list
                res_lst = []
                for info in infos:
                    t = info.to_dict()
                    if 'img_id' in t:
                        img_info = yield ImgDao.get_by_id(None, conn, t['img_id'])
                        if img_info:
                            t['img_url'] = img_info.imgurl
                    elif 'img_key' in t:
                        img_info = yield ImgDao.get_by_col(None, conn, t['img_key'], where_col='img_key', col_str=True)
                        if img_info:
                            t['img_url'] = img_info.imgurl
                    res_lst.append(t)
            data = {'code': 1, 'msg': 'ok', 'page_num': 10, 'all_len': all_len, 'data': res_lst}
            data = json.dumps(data, indent=4, cls=MyJsonEncoder, ensure_ascii=False)
            self.finish(data)

    @tornado.gen.coroutine
    @tornado.web.authenticated
    def post(self):
        dic = {}
        logging.info("新增dic如下")
        for key, value in self.request.arguments.iteritems():
            if key in self.post_filter_key_lst:
                logging.info("跳过key=%s" % key)
                continue

            dic[key] = value[0]
            logging.info("%s=%s" % (key, value[0]))

        self.set_header("Content-Type", "application/json; charset=UTF-8")

        pool = self.pools[0]
        with (yield pool.Connection()) as conn:
            try:
                new_id = yield self.DataDao.new(None, conn, dic)
                yield conn.commit()

                info = yield self.DataDao.get_by_id(None, conn, new_id)
                dic = info.to_dict()
                data = {'code': 1, 'msg': 'ok', 'data': dic}
            except tornado.gen.Return:
                raise
            except Exception, ex:
                logging.error(ex, exc_info=1)
                yield conn.rollback()
                data = {'code': -1, 'msg': str(ex)}

        data = json.dumps(data, indent=4, cls=MyJsonEncoder, ensure_ascii=False)
        self.finish(data)

    @tornado.gen.coroutine
    @tornado.web.authenticated
    def delete(self):
        del_id = int(self.get_argument('id', 0))
        logging.info("删除id=%s" % del_id)

        self.set_header("Content-Type", "application/json; charset=UTF-8")
        data = {'code': 1, 'msg': 'ok'}

        pool = self.pools[0]
        with (yield pool.Connection()) as conn:
            try:
                yield self.DataDao.delete(None, conn, del_id)
                yield conn.commit()
            except tornado.gen.Return:
                raise
            except Exception, ex:
                logging.error(ex, exc_info=1)
                yield conn.rollback()
                data = {'code': -1, 'msg': str(ex)}

        data = json.dumps(data, indent=4, cls=MyJsonEncoder, ensure_ascii=False)
        self.finish(data)

    @tornado.gen.coroutine
    @tornado.web.authenticated
    def put(self):
        dic = {}
        logging.info("更新dic如下")
        for key, value in self.request.arguments.iteritems():
            if key in self.put_filter_key_lst:
                logging.info("跳过key=%s" % key)
                continue

            dic[key] = value[0]
            logging.info("%s=%s" % (key, value[0]))

        self.set_header("Content-Type", "application/json; charset=UTF-8")

        pool = self.pools[0]
        with (yield pool.Connection()) as conn:
            try:
                yield self.DataDao.update(None, conn, dic)
                yield conn.commit()

                info = yield self.DataDao.get_by_id(None, conn, dic['id'])
                dic = info.to_dict()

                data = {'code': 1, 'msg': 'ok', 'data': dic}
            except tornado.gen.Return:
                raise
            except Exception, ex:
                logging.error(ex, exc_info=1)
                yield conn.rollback()
                data = {'code': -1, 'msg': str(ex)}

        data = json.dumps(data, indent=4, cls=MyJsonEncoder, ensure_ascii=False)
        self.finish(data)

    def get_helper_merge_data(self, infos, col_infos):
        """
        因为有可能不同列搜出来有相同的数据，我们需要去重。
        用归并算法去重

        用归并算法的merge模块，来合并两个list
        :param infos:  左边list
        :param col_infos: 右边list
        :return: 合并后的左边list
        """
        tmp_infos = []
        left_cnt = right_cnt = 0
        while left_cnt < len(infos) and right_cnt < len(col_infos):
            if infos[left_cnt].id < col_infos[right_cnt].id:
                tmp_infos.append(infos[left_cnt])
                left_cnt += 1
            elif infos[left_cnt].id > col_infos[right_cnt].id:
                tmp_infos.append(col_infos[right_cnt])
                right_cnt += 1
            else:
                # 进入此处逻辑表示两个列表的哨兵相等，则两个列表同时跳过
                tmp_infos.append(infos[left_cnt])
                left_cnt += 1
                right_cnt += 1
        while left_cnt < len(infos):
            tmp_infos.append(infos[left_cnt])
            left_cnt += 1
        while right_cnt < len(col_infos):
            tmp_infos.append(col_infos[right_cnt])
            right_cnt += 1

        # 再把tmp_info赋值给infos，继续下一轮的合并（如果有下一轮的话）
        infos = tmp_infos
        return infos

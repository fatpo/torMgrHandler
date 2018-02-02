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
        page = int(self.get_argument('page', 1))
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
                    infos = yield self.DataDao.search_by_col(None, conn, key, col="name")
                    all_len = len(infos)
                else:
                    infos = yield self.DataDao.get_all(None, conn, page)
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
                        img_info = yield ImgDao.get_by_col(None, conn, t['img_key'], where_col='img_key')
                        if img_info:
                            t['img_url'] = img_info.imgurl
                    res_lst.append(t)
            data = {'code': 1, 'msg': 'ok', 'page_num': 10, 'all_len': all_len, 'data': res_lst}
            data = json.dumps(data, indent=4, cls=MyJsonEncoder, ensure_ascii=False)
            self.finish(data)

    @tornado.gen.coroutine
    @tornado.web.authenticated
    def post(self):
        dic = self.request.arguments
        logging.info("新增dic如下")
        for key, value in dic.iteritems():
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
        dic = self.request.arguments
        logging.info("更新dic如下")
        for key, value in dic.iteritems():
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

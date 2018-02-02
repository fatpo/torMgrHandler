# coding=utf-8
from apihandler.H5BaseMgr import H5BaseHandler
from dao.Student import StudentDao


class StudentMgrHandler(H5BaseHandler):
    """
        学生管理的handler
        JSON数据返回
    """
    DataDao = StudentDao
    HtmlPath = "backend/gongxiu/index.html"

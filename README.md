# torMgrHandler
基于tornado的restful风格的管理后台利器，5分钟配置出一个管理模块...     
实际上一个项目的管理后台模块可能有上百个，什么学生管理、年级管理、班级管理、寝室管理、然后图书管理...    
但是大部分代码是可重复，需要定制的机会比较少...    
为了pythonic，我们用配置来产出管理模块，有趣..   

# 模拟场景
要写一个学生管理，满足最简单的增删改查...    

1、写sql：
```
CREATE TABLE `student` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(128) not NULL  DEFAULT '' comment 'student's name',
  `age` int(11) not NULL  DEFAULT 0 comment 'student's age',
  `del_flag` int(11) NOT NULL DEFAULT 0 comment 'soft delete flag，0-normal，1-deleted',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP comment 'create time',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP comment 'last update time',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

```
2、定义一个info（你也可以用字典直接操作）:
```
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
```
3、配置出一个dao（基于我的项目[torBizMysqlDao](https://github.com/emaste-r/torBizMysqlDao "Title")）:
```
class StudentDao(BaseDao):
    DataInfo = StudentInfo
    table_name = 'student'  # table name
    escape_list = ['name']  # the list need to be escaped 
    quot_list = ['create_time', 'update_time']  # the list requires quoted
    not_append_list = ['del_flag']  # int list like: img_id
    append_list = ['age']  # int list, but sometimes need to += n, like: add_cnt = add_cnt+10, view_cnt=view_cnt+1
```
4、配置一个api handler:
```
# coding=utf-8
from apihandler.H5BaseMgr import H5BaseHandler
from dao.Student import StudentDao


class StudentMgrHandler(H5BaseHandler):
    """
        学生管理的handler
        JSON数据返回
    """
    DataDao = StudentDao
    HtmlPath = "backend/student/index.html"  # 这里当然需要前端写好了html...

```
5、配置路由
```
class Application(tornado.web.Application):
    def __init__(self):
        app_settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            debug=False,
            login_url="/backend/login",
            cookie_secret="xxx",
            compiled_template_cache=False,
        )

        # URL Mapping
        handlers = [
            (r"/backend/student", StudentMgrHandler),
        ]

        def write_error(self, stat, **kw):
            self.write(u'哎呀，url迷路了~')

        tornado.web.RequestHandler.write_error = write_error

        # Init
        super(Application, self).__init__(handlers, **app_settings)
```
6、
```
python main.py --port=9999
```

7、
```
http://127.0.0.1:9999/backend/student
```

# 接口文档
## 1、获取列表
地址：
```
/backend/student
```
方法：
```
GET
```
参数：
```
cmd：string，可不带，不带表示渲染html
     带get，表示获取 list，
key：string，搜索key
page：int，分页
```
返回：
```
{
    "msg": "ok",
    "data": [
       {
        "name": "tom",
        "update_time": "2018-01-30 11:30:03",
        "create_time": "2018-01-30 11:16:10",
        "del_flag": 0，
        "id": 1
    }
    ],
    "code": 1,
    "page_num": 10,
    "all_len": 1
}
```


## 2、删除
地址：
```
/backend/student
```
方法：
```
DELETE
```
参数：
```
id: int, id
```
返回：
```
{
    'code': 1, 
    'msg': 'ok'
}
```

## 3、新增
地址：
```
/backend/student
```
方法:
```
POST
```
参数：
```
name: string, 名字
age: int， 年龄
```
返回：
```
{
    "msg": "ok",
    "code": 1,
    "data": {
        "name": "tom",
        "update_time": "2018-01-30 11:30:03",
        "create_time": "2018-01-30 11:16:10",
        "del_flag": 0，
        "id": 1
    }
}
```
## 4、更新
地址：
```
/backend/student
```
方法:
```
PUT
```
参数：
```
id: int, id
name: string, 名字
aget: int，年龄
```
返回：
```
{
    "msg": "ok",
    "code": 1,
    "data": {
        "name": "tom",
        "update_time": "2018-01-30 11:30:03",
        "create_time": "2018-01-30 11:16:10",
        "del_flag": 0，
        "id": 1
    }
}
```




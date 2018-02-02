# coding=utf-8
import logging
import os
import signal
import time

import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado.options import define, options

from apihandler.StudentMgr import StudentMgrHandler


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


def main():
    # 配置main.py的命令
    define("port", default=None, help="Run server on a specific port, mast input",
           type=int)

    # start from cmd
    options.parse_command_line()
    try:
        if options.port == None:
            options.print_help()
            return
    except:
        print 'Usage: python main.py --port=8000'
        return

    # 信号监听
    def sig_handler(sig, frame):
        logging.warning('Caught signal: %s', sig)
        tornado.ioloop.IOLoop.instance().add_callback(shutdown)

    # 关闭服务器
    def shutdown():
        logging.info('Stopping http server')
        http_server.stop()

        logging.info('server will shutdown in 2 seconds ...')
        io_loop = tornado.ioloop.IOLoop.instance()

        deadline = time.time() + 2

        def stop_loop():
            now = time.time()
            if now < deadline and (io_loop._callbacks or io_loop._timeouts):
                io_loop.add_timeout(now + 1, stop_loop)
            else:
                io_loop.stop()
                logging.info('Shutdown')

        stop_loop()

    global http_server
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)

    # 按Ctrl+C退出程序
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)

    # start server
    tornado.ioloop.IOLoop.instance().start()
    logging.info('Exit Master')


if __name__ == '__main__':
    main()

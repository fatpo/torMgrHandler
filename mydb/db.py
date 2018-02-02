# coding=utf-8
import pymysql
import tormysql
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

db_user = "app"
db_host = "127.0.0.1"
db_pass = "app_pass"
db_name = "myapp"

# tormysql
app_pool = tormysql.ConnectionPool(
    max_connections=80,  # max open connections
    idle_seconds=180,  # conntion idle timeout time, 0 is not timeout 连接空闲超过idle_seconds 后会自动关闭回收连接的
    wait_connection_timeout=3,  # wait connection timeout
    host=db_host,
    user=db_user,
    passwd=db_pass,
    db=db_name,
    charset="utf8",
    cursorclass=pymysql.cursors.DictCursor,
)

# sqlalchemy
app_engine = create_engine('mysql://%s:%s@%s/%s?charset=utf8' % (db_user, db_pass, db_host, db_name),
                           encoding='utf-8', echo=False,
                           poolclass=QueuePool, max_overflow=100, pool_size=1, pool_recycle=10, pool_timeout=30)

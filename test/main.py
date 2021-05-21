import pymysql

from pymysqlpool.dbpool import DBPool

pool = DBPool(
    max_connections=10,  # 连接池允许的最大连接数，0和None表示不限制连接数
    set_session=[f'SET time_zone = "+8:00"', 'SET autocommit=1'],  # 开始会话前执行的命令列表。如：["set datestyle to …", "set time zone …"]
    ping=1,  # ping 探活。 0=None=never, 1=default=requested,2=cursor created, 4=query executed,7=always
    host="192.168.12.86",
    port=30000,
    user="root",
    password="introcks1234",
    database="vesion_book_console",
    charset="utf8"
)


def connect1():
    conn1 = pool.connect()
    try:
        cursor = conn1.cursor(pymysql.cursors.DictCursor)
        cursor.execute("select * from t_menu limit 1")
        result = cursor.fetchall()
        print(result)
        cursor.close()
    finally:
        conn1.close()


def connect2():
    conn2 = pool.connect()
    try:
        cursor = conn2.cursor(pymysql.cursors.DictCursor)
        cursor.execute("select * from t_menu limit 1")
        result = cursor.fetchall()
        print(result)
        cursor.close()
    finally:
        conn2.close()


def connect3():
    conn3 = pool.connect()
    try:
        conn3.begin()
        cursor = conn3.cursor(pymysql.cursors.DictCursor)
        cursor.execute("update t_menu set creator='111' where id=1")
        cursor.execute("update t_menu set creator='222' where id=2")
        conn3.commit()
        cursor.execute("select creator from t_menu where id = 1")
        result = cursor.fetchall()
        print(result)
    finally:
        conn3.close()


if __name__ == '__main__':
    connect1()
    connect2()
    connect3()

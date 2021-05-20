# Installation
```shell script
pip install pymysql-dbpool
```

# Create Mysql Pool
```python
from pymysqlpool.pooled_db import PooledDB

pool = PooledDB(
    max_connections=10,  # 连接池允许的最大连接数，0和None表示不限制连接数
    set_session=[f'SET time_zone = "+8:00"', 'SET autocommit=1'],  # 开始会话前执行的命令列表。如：["set datestyle to …", "set time zone …"]
    ping=1,  # ping 探活。 0=None=never, 1=default=requested,2=cursor created, 4=query executed,7=always
    host="127.0.0.1",
    port=3306,
    user="root",
    password="admin",
    database="testdb",
    charset="utf8"
)
```
# Execute sql command
### select
```python
conn = pool.connect()
try:
    cursor = conn.cursor()
    cursor.execute("select * from table")
    result = cursor.fetchall()
    cursor.close()
finally:
    # 这里回收连接
    conn.close()
```
### insert
创建pool的时候，如果设置了自动提交，即`set_session`参数包含`SET autocommit=1`语句，
那么insert之后无需调用commit()，否则需要调用commit()手动提交。
```python
conn = pool.connect()
try:
    cursor = conn.cursor()
    cursor.execute("insert into table value(...)")
    # conn.commit()
    cursor.close()
finally:
    # 这里回收连接
    conn.close()
```

### update
创建pool的时候，如果设置了自动提交，即`set_session`参数包含`SET autocommit=1`语句，
那么update之后无需调用commit()，否则需要调用commit()手动提交。
```python
conn = pool.connect()
try:
    cursor = conn.cursor()
    cursor.execute("update table set col='val' where condition")
    # conn.commit()
    cursor.close()
finally:
    # 这里回收连接
    conn.close()
```

### transaction
事务，调用`begin()`和`commit()`分别开启和提交事务
```python
conn = pool.connect()
try:
    cursor = conn.cursor()
    # start transaction
    conn.begin()
    cursor.execute("update table set col1=val1 where condition")
    cursor.execute("update table set col2=val2 where condition")
    # commit transaction
    conn.commit()
    cursor.close()
finally:
    # 这里回收连接
    conn.close()
```



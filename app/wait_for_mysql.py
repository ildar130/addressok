import sys, time
import pymysql
import conf

db_root_password = conf.db_root_password

dbconn = None

# Пытаемся приконнектиться в течение 120 секунд
for i in range(0, 120, 1):
    try:
        dbconn = pymysql.connect(host=conf.db_host, user='root',
            passwd=db_root_password, db='mysql', port=conf.db_port,
            charset='utf8')
        break
    except pymysql.err.OperationalError as err:
        # если ошибка "Can't connect to MySQL server..."
        if err.args[0] == 2003:
            print('MySQL is not available. Waiting...')
            time.sleep(1)
        else:
            raise

if dbconn is None:
    print('Could not connect to MySQL server. Exiting.')
    exit(1)

dbconn.close()

print('Connected to MySQL.')

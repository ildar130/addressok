"""Этот скрипт выполняется при запуске сервиса."""

import sys
import pymysql
import conf

db_root_password = conf.db_root_password

dbconn = None

# Пытаемся приконнектиться в течение 10 секунд
for i in range(0, 10, 1):
    try:
        dbconn = pymysql.connect(host=conf.db_host, user='root',
            passwd=db_root_password, db='mysql', port=conf.db_port,
            charset='utf8')
        break
    except pymysql.err.OperationalError as err:
        # если ошибка "Can't connect to MySQL server..."
        if err.args[0] == 2003:
            time.sleep(1)
        else:
            raise

if dbconn is None:
    print('Could not connect to MySQL server. Exiting...')
    exit()

cursor = dbconn.cursor()

# Проверяем, существует ли пользователь
sql = """SELECT EXISTS(SELECT 1 FROM mysql.user WHERE user = '%(db_user)s')
    """ % {
        'db_user': conf.db_user,
        'db_password': conf.db_password,
        'db_name': conf.db_name,
    }
cursor.execute(sql)
cnt = cursor.fetchone()[0]
if cnt == 0:
    # Создаём пользователя
    sql = """CREATE USER '%(db_user)s'@'%%' IDENTIFIED BY '%(db_password)s';
        """ % {
            'db_user': conf.db_user,
            'db_password': conf.db_password,
        }
    cursor.execute(sql)
    dbconn.commit()

# Создаём базу данных, если она не существует
sql = """CREATE DATABASE IF NOT EXISTS addressok
        CHARACTER SET utf8 COLLATE utf8_general_ci;
    GRANT ALL PRIVILEGES ON %(db_name)s.* TO '%(db_user)s'@'%%';
    FLUSH PRIVILEGES;
    """ % {
        'db_user': conf.db_user,
        'db_name': conf.db_name,
    }
cursor.execute(sql)

dbconn.commit()
cursor.close()
dbconn.close()

# Подключаемся от имени созданного пользователя и создаём таблицу OPTIONS

dbconn = pymysql.connect(host=conf.db_host, user=conf.db_user,
    passwd=conf.db_password, db=conf.db_name, port=conf.db_port,
    charset='utf8')
cursor = dbconn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS options (
        id INTEGER NOT NULL AUTO_INCREMENT,

        db_version INTEGER DEFAULT 0,
        fias_ver_date TEXT,

        PRIMARY KEY(id)
    )""")

dbconn.commit()
cursor.close()
dbconn.close()

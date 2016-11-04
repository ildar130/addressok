"""Скрипт проверяет наличие новой версии БД ФИАС и при необходимости
скачивает архив с новой версией и обновляет данные в БД."""

import os, subprocess, time
from datetime import datetime
import urllib.request
import pymysql
import initializer
import conf

def ensure_dir(dirname):
    """Создаёт папку, если её нет."""
    if not os.path.exists(dirname):
        os.makedirs(dirname)

def drop_tables(conn, db_version):
    """Удаляет таблицы старой версии."""
    cur = conn.cursor()
    cur.execute('DROP TABLE addrobj_v%s' % db_version)
    cur.execute('DROP TABLE socrbase_v%s' % db_version)
    cur.execute('DROP TABLE zipcodes_v%s' % db_version)
    cur.execute('DROP TABLE ziplinks_v%s' % db_version)
    cur.close()

# Папка для XML с исходными данными
data_dir = conf.data_dir

dbconn = None

def connect_to_db():
    global dbconn
    dbconn = pymysql.connect(host=conf.db_host, user=conf.db_user,
        passwd=conf.db_password, db=conf.db_name, port=conf.db_port,
        charset='utf8')

# Пытаемся приконнектиться в течение 10 секунд
for i in range(0, 10, 1):
    try:
        connect_to_db()
        break
    except pymysql.err.OperationalError as err:
        # если ошибка "Can't connect to MySQL server..."
        if err.args[0] == 2003:
            print('Could not connect to MySQL server. Waiting...')
            time.sleep(1)
        else:
            raise

if dbconn is None:
    print('Could not connect to MySQL server. Exiting...')
    exit()

cursor = dbconn.cursor(pymysql.cursors.DictCursor)

cursor.execute("""CREATE TABLE IF NOT EXISTS options (
        id INTEGER NOT NULL AUTO_INCREMENT,

        db_version INTEGER DEFAULT 0,
        fias_ver_date TEXT,

        PRIMARY KEY(id)
    )""")

ensure_dir(data_dir)

do_create_options = False
# Дата последней актуальной версии БД с сайта ФИАС
cur_ver_date = ''
# Следующий номер версии БД
next_db_version = 1
cursor.execute("SELECT db_version, fias_ver_date FROM options LIMIT 1")
row = cursor.fetchone()
if row is not None:
    cur_ver_date = row['fias_ver_date'] if row['fias_ver_date'] is not None else ''
    next_db_version = row['db_version'] + 1
else:
    # Если в таблице OPTIONS нет записей,
    # то вместо UPDATE нужно выполнить INSERT
    do_create_options = True

dbconn.commit()
dbconn.close()

# Получаем дату последней актуальной версии БД с сайта ФИАС
resp = urllib.request.urlopen('http://fias.nalog.ru/Public/Downloads/Actual/VerDate.txt')
data = resp.read()
fias_ver_date = data.decode('utf-8')

# Если дата последней актуальной версии БД с сайта ФИАС отличается,
# то запускаем процесс обновления
if fias_ver_date != cur_ver_date:
    # Скачиваем архив
    print('New version detected')
    print('Downloading file...')
    rar_fname = os.path.join(data_dir, 'fias_xml.rar')
    os.system('rm -rf %s/*' % data_dir)
    os.system('wget http://fias.nalog.ru/Public/Downloads/Actual/fias_xml.rar -P %s' % data_dir)
    print('Done.')

    # Имя XML-файла с адресными объектами
    addrobj_file_name = ''
    # Имя XML-файла с сокращениями
    socr_file_name = ''

    # Получаем список файлов
    files_list = subprocess.check_output('unrar lb %s' % rar_fname,
        stderr=subprocess.STDOUT, shell=True).splitlines()
    for filename in files_list:
        if filename.decode('utf-8').startswith(('AS_ADDROBJ_', 'AS_SOCRBASE_')):
            # Распаковываем
            fname = os.path.join(data_dir, filename.decode('utf-8'))
            cmd_str = "unrar e %s %s %s" % (rar_fname,
                filename.decode('utf-8'), data_dir)
            os.system(cmd_str)

            if filename.decode('utf-8').startswith('AS_ADDROBJ_'):
                addrobj_file_name = fname
            elif filename.decode('utf-8').startswith('AS_SOCRBASE_'):
                socr_file_name = fname

    t1 = datetime.now()

    connect_to_db()

    init = initializer.AddressOKInitializer(dbconn, next_db_version)

    # Создаём таблицы в БД
    init.create_tables()
    
    # Загружаем данные
    init.load_address_objects(addrobj_file_name)
    init.load_socr(socr_file_name)

    # Прочие необходимые действия (заполнение поля parentid, индексов,
    # наименований адресных объектов и т.д.)
    init.fill_parent_ids()
    init.fill_zip_codes()
    init.fill_zip_links()
    init.fill_socr_codes()
    init.fill_socr_names()
    init.fill_addrobj_socr()
    init.fill_socr_diplaynames()
    init.fill_good_names()

    t2 = datetime.now()
    # Время инициализации
    print("Initializing time:", t2 - t1)

    # Увеличиваем на 1 номер текущей версии
    if do_create_options:
        cursor.execute("""INSERT INTO options (db_version, fias_ver_date)
            VALUES (%(db_version)s, '%(ver_date)s')
            """ % {
                'db_version': next_db_version,
                'ver_date': fias_ver_date
            })
    else:
        cursor.execute("""UPDATE options
            SET db_version = %(db_version)s,
                fias_ver_date = '%(ver_date)s'
            """ % {
                'db_version': next_db_version,
                'ver_date': fias_ver_date
            })

    # Пауза перед удалением таблиц для того, чтобы завершились
    # запросы к сервису, выполняемые в данный момент
    print('Sleeping... Z-z-z...')
    time.sleep(10)

    # Удаляем таблицы предыдущей версии
    if next_db_version > 1:
        drop_tables(dbconn, next_db_version-1)

    dbconn.commit()
    dbconn.close()
else:
    print('Already up-to-date.')


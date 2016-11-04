"""Этот скрипт производит начальную инициализацию БД и должен быть
выполнен один раз."""
import os
import pymysql
import initializer

db = pymysql.connect(host='mysql', user='addressok', passwd='123',
    db='addressok', port=3306, charset='utf8')

# Папка для XML с исходными данными
xmldir = '/data/srcxml'
addrobj_file = ''
socrbase_file = ''
for fname in os.listdir(xmldir):
	# Файл с адресными объектами
    if fname.lower().startswith('as_addrobj_') and fname.lower().endswith('.xml'):
        addrobj_file = fname
	# Файл с сокращениями
    elif fname.lower().startswith('as_socrbase_') and fname.lower().endswith('.xml'):
        socrbase_file = fname

init = initializer.AddressOKInitializer(db, 1)
init.create_tables()
init.load_address_objects(os.path.join(xmldir, addrobj_file))
init.load_socr(os.path.join(xmldir, socrbase_file))
init.fill_parent_ids()
init.fill_zip_codes()
init.fill_zip_links()
init.fill_socr_codes()
init.fill_socr_names()
init.fill_addrobj_socr()
init.fill_socr_diplaynames()
init.fill_good_names()

cur = db.cursor(pymysql.cursors.DictCursor)

# Вставляем начальные данные в таблицу OPTIONS
sql = "DELETE FROM options"
cur.execute(sql)
sql = "INSERT INTO options (db_version, fias_ver_date) VALUES (1, '')"
cur.execute(sql)
db.commit()

cur.close()

db.close()

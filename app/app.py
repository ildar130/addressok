import json, traceback, time
import pymysql
from flask import Flask
from flask import request
import getter
import conf

app = Flask(__name__)

# Logging
import logging
file_logging_handler = logging.FileHandler(conf.log_file)
file_logging_handler.setLevel(logging.INFO)
file_logging_handler.setLevel(logging.DEBUG)
app.logger.addHandler(file_logging_handler)

dbconn = None

def connect_to_mysql():
    """Connects to MySQL and returns the connection."""
    return pymysql.connect(host=conf.db_host, user=conf.db_user,
        passwd=conf.db_password, db=conf.db_name, port=conf.db_port,
        charset='utf8')

# Пытаемся приконнектиться в течение 10 секунд
for i in range(0, 10, 1):
    try:
        dbconn = connect_to_mysql()
        break
    except pymysql.err.OperationalError as err:
        # если ошибка "Can't connect to MySQL server..."
        if err.args[0] == 2003:
            print(traceback.format_exc())
            time.sleep(1)
        else:
            raise

if dbconn is None:
    app.logger.error('Could not connect to MySQL server. Exiting...')
    exit()

@app.route('/', methods=['POST'])
def get_addr():
    res = {}
    global dbconn
    try:
        gtr = getter.AddressOKGetter(dbconn)
    except pymysql.err.OperationalError as err:
        # если ошибка "Lost connection to MySQL server during query" (2013)
        # или "MySQL server has gone away" (2006)
        if err.args[0] in (2013, 2006):
            time.sleep(0.1)
            dbconn = connect_to_mysql()
            gtr = getter.AddressOKGetter(dbconn)
        else:
            raise

    try:
        # Запрос адресных данных по почтовому индексу
        if request.form['request_type'] == 'zip':
            res = gtr.get_addr_objects_by_zip_code(request.form['zip_code'])
            res['result'] = 'ok'
        # Запрос адресных данных по всем полям
        elif request.form['request_type'] == 'all':
            res = gtr.get_addr_objects_raw(int(request.form['region_id']),
                int(request.form['district_id']), int(request.form['place_id']),
                int(request.form['street_id']), request.form['zip_code'])
            res['result'] = 'ok'
    except Exception as e:
        # Logging error
        app.logger.error('EXCEPTION!\n'+str(e)+'\n'+traceback.format_exc())

        res['result'] = 'error'
        res['error_message'] = 'Internal AddressOK server error'

    return json.dumps(res)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=14000, debug=True)
    dbconn.close()
    print('\nDone.')
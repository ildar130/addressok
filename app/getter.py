from collections import OrderedDict
import hashlib # ToDo: remove this
import pymysql

class AddressOKGetter:
    """Класс, предоставляющий функционал для получения
    адресной информации из БД."""

    def __init__(self, dbconn, version=None):
        self.dbconn = dbconn
        self.version = version if version is not None else self._get_version()
        self.version_suffix = '_v'+str(self.version)

    def _get_version(self):
        cursor = self.dbconn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT db_version FROM options LIMIT 1")
        row = cursor.fetchone()
        res = row['db_version'] if row is not None else 0
        cursor.close()
        return res

    def get_parent_ids(self, ao_id):
        """Возвращает список ID для адресного объекта с данным ID."""
        ret = []

        cursor = self.dbconn.cursor(pymysql.cursors.DictCursor)
        sql = """SELECT parentid FROM addrobj%(version_suffix)s
            WHERE id = '%(ao_id)s'""" % {
                'version_suffix': self.version_suffix,
                'ao_id': ao_id
            }
        cursor.execute(sql)
        row = cursor.fetchone()
        cursor.close()

        if row is not None and row['parentid'] != 0:
            ret.append(row['parentid'])
            ret.extend(self.get_parent_ids(row['parentid']))

        return ret

    def get_zip_codes(self, ao_id):
        """Возвращает список почтовых индексов для
        адресного объекта с данным ID."""
        res = []
        cur1 = self.dbconn.cursor(pymysql.cursors.DictCursor)

        sql = """SELECT
                zc.zip
            FROM ziplinks%(version_suffix)s zl
            INNER JOIN zipcodes%(version_suffix)s zc ON zl.zipid = zc.id
            WHERE
                zl.aoid = %(ao_id)s""" % {
                    'version_suffix': self.version_suffix,
                    'ao_id': ao_id
                }
        cur1.execute(sql)
        res = [row['zip'] for row in cur1]

        cur1.close()

        return res

    def get_addr_objects_by_zip_code(self, zip_code):
        """Возвращает адресную информацию по почтовому индексу."""
        res = {
            'fill': {
                'zip': zip_code,
                'region': {'label': '', 'value': 0},
                'district': {'label': '', 'value': 0},
                'place': {'label': '', 'value': 0},
                'street': {'label': '', 'value': 0},
            },
            'suggest': {
                'region': [],
                'district': [],
                'place': [],
                'street': [],
            }
        }

        cur1 = self.dbconn.cursor(pymysql.cursors.DictCursor)

        aolevels = OrderedDict([
            (1, 'region'),
            (3, 'district'),
            (4, 'place'),
            (6, 'place'),
            (7, 'street'),
        ])

        res_lists = {
            'region': [],
            'district': [],
            'place': [],
            'street': [],
        }

        cur1 = self.dbconn.cursor(pymysql.cursors.DictCursor)
        sql = """SELECT
                ao.id,
                ao.aolevel,
                ao.displayname
            FROM zipcodes%(version_suffix)s zc
            INNER JOIN ziplinks%(version_suffix)s zl ON zl.zipid = zc.id
            INNER JOIN addrobj%(version_suffix)s ao ON zl.aoid = ao.id
            WHERE
                zc.zip = '%(zip_code)s'
                and aolevel in (1,3,4,6,7)
            ORDER BY ao.aolevel, ao.formalname""" % {
                'version_suffix': self.version_suffix,
                'zip_code': zip_code
            }
        cur1.execute(sql)
        for row in cur1:
            res['suggest'][aolevels[row['aolevel']]].append({
                'value': row['id'],
                'label': row['displayname']
            })
        cur1.close()

        for key, items in res['suggest'].items():
            if len(items) == 1:
                res['fill'][key] = res['suggest'][key][0]
                res['suggest'][key] = []
        return res

    def get_initial_addr_objects(self):
        """Возвращает начальную адресную информацию (для инициализации
        формы ввода адреса)."""
        res = {
            'fill': {
                'zip': '',
                'region': {'label': '', 'value': 0},
                'district': {'label': '', 'value': 0},
                'place': {'label': '', 'value': 0},
                'street': {'label': '', 'value': 0},
            },
            'suggest': {
                'region': [],
                'district': [],
                'place': [],
                'street': [],
            }
        }

        cur1 = self.dbconn.cursor(pymysql.cursors.DictCursor)

        sql = """SELECT
                ao.id,
                ao.aolevel,
                ao.displayname,
                ao.formalname
            FROM addrobj%(version_suffix)s ao
            WHERE
                ao.aolevel = 1
            ORDER BY ao.formalname""" % {
                'version_suffix': self.version_suffix
            }
        cur1.execute(sql)

        for row in cur1:
            res['suggest']['region'].append({
                'value': row['id'],
                'label': row['displayname']
            })

        cur1.close()

        return res

    def get_addr_objects(self, ao_id, zip_code):
        """Возвращает адресную информацию по ID адресного объекта
        и почтовому индексу."""

        if ao_id == 0 and zip_code.strip() == '':
            return self.get_initial_addr_objects()

        res = {
            'fill': {
                'zip': '',
                'region': {'label': '', 'value': 0},
                'district': {'label': '', 'value': 0},
                'place': {'label': '', 'value': 0},
                'street': {'label': '', 'value': 0},
            },
            'suggest': {
                'region': [],
                'district': [],
                'place': [],
                'street': [],
            }
        }

        cur1 = self.dbconn.cursor(pymysql.cursors.DictCursor)

        aolevels = OrderedDict([
            (1, 'region'),
            (3, 'district'),
            (4, 'place'),
            (6, 'place'),
            (7, 'street'),
        ])

        ao_level = 0

        ids = self.get_parent_ids(ao_id)
        ids.insert(0, ao_id)

        # Однозначно заполненные данные
        ids_list_str = ', '.join([str(id) for id in ids])
        sql = """SELECT
                id,
                aolevel,
                displayname,
                formalname
            FROM addrobj%(version_suffix)s
            WHERE
                id in (%(ids_list_str)s)
            ORDER BY aolevel""" % {
                'version_suffix': self.version_suffix,
                'ids_list_str': ids_list_str
            }
        cur1.execute(sql)
        for row in cur1:
            res['fill'][aolevels[row['aolevel']]]['value'] = row['id']
            res['fill'][aolevels[row['aolevel']]]['label'] = row['displayname']

            if row['id'] == ao_id:
                ao_level = row['aolevel']

        # Следующие уровни адресных объектов
        next_levels = tuple()
        if ao_level == 1:
            next_levels = (3,)
        elif ao_level == 3:
            next_levels = (4, 6)
        elif ao_level in (4, 6):
            next_levels = (7,)

        # Получаем данные следующих уровней для подсказок
        if len(next_levels) > 0:
            # Получаем ID почтового индекса
            sql = """SELECT
                    *
                FROM zipcodes%(version_suffix)s
                WHERE
                    zip = '%(zip_code)s'""" % {
                        'version_suffix': self.version_suffix,
                        'zip_code': zip_code
                    }
            cur1.execute(sql)
            r = cur1.fetchone()
            zip_id = r['id'] if r is not None else 0

            aolevels_str = ', '.join([str(l) for l in next_levels])
            # ToDo: remove suggest_index
            suggest_index = aolevels[next_levels[0]]
            if zip_id > 0:
                sql = """SELECT
                        ao.id,
                        ao.aolevel,
                        ao.displayname,
                        ao.formalname
                    FROM addrobj%(version_suffix)s ao
                    INNER JOIN ziplinks%(version_suffix)s zl ON ao.id = zl.aoid
                    WHERE
                        ao.parentid = %(ao_id)s
                        -- and ao.aolevel in (%(aolevels_str)s)
                        and ao.aolevel in (1,3,4,6,7)
                        and zl.zipid = %(zip_id)s
                    ORDER BY ao.formalname""" % {
                        'version_suffix': self.version_suffix,
                        'ao_id': ao_id,
                        'aolevels_str': aolevels_str,
                        'zip_id': zip_id,
                    }
            else:
                sql = """SELECT
                        id,
                        aolevel,
                        displayname,
                        formalname
                    FROM addrobj%(version_suffix)s ao
                    WHERE
                        ao.parentid = %(ao_id)s
                        -- and ao.aolevel in (%(aolevels_str)s)
                        and ao.aolevel in (1,3,4,6,7)
                    ORDER BY ao.formalname
                    """ % {
                        'version_suffix': self.version_suffix,
                        'ao_id': ao_id,
                        'aolevels_str': aolevels_str
                    }
            cur1.execute(sql)
            for row in cur1:
                # ToDo: remove commented-out lines
                # res['suggest'][suggest_index].append(
                #     {'value': row['id'], 'label': row['displayname']})
                res['suggest'][aolevels[row['aolevel']]].append(
                    {'value': row['id'], 'label': row['displayname']})

        # Получаем почтовые индексы
        if zip_code.strip() == '':
            zip_codes = self.get_zip_codes(ao_id)
            # Если почтовый индекс один, заполняем его
            if len(zip_codes) == 1:
                res['fill']['zip'] = zip_codes[0]
        else:
            res['fill']['zip'] = zip_code

        # ToDo: remove commented-out lines
        # if ao_level == 4:
        #     ao_level = 6
        # aolevels_list = list(aolevels.keys())
        # if ao_level in aolevels_list:
        #     print(aolevels_list.index(ao_level))
        # else:
        #     print('oops')

        cur1.close()

        return res

    def get_addr_objects_raw(self, region_id, district_id, place_id, street_id, zip_code):
        """Возвращает адресные объекты."""
        ao_id = 0
        if street_id and street_id > 0:
            ao_id = street_id
        elif place_id and place_id > 0:
            ao_id = place_id
        elif district_id and district_id > 0:
            ao_id = district_id
        elif region_id and region_id > 0:
            ao_id = region_id

        return self.get_addr_objects(ao_id, zip_code)

    # ToDo: remove this
    def get_password_hash(self, password, salt):
        """Returns hash from password and salt."""
        static_salt = 'zJNm=d1YeJaZ+Q*taLF#iQQai2HxRZKb'

        full_pass_and_salt = password+salt+static_salt
        password_hash = hashlib.sha256(full_pass_and_salt.encode('utf-8')).hexdigest()
        # password_hash = hashlib.sha512(full_pass_and_salt.encode('utf-8')).hexdigest()

        return password_hash

    # ToDo: remove this
    def check_authorization_old(self, user, password):
        """Returns True, if password is correct, False otherwise.
        Returns None, if such user is not found in the DB."""
        res = ''
        cur = self.dbconn.cursor(pymysql.cursors.DictCursor)
        sql = """SELECT password_salt, password_hash, request_count FROM accounts
            WHERE username = '%(username)s'""" % {'username': user}
        cur.execute(sql)
        row = cur.fetchone()
        if row is None:
            res = 'unknown_login'
        else:
            pass_hash = self.get_password_hash(password, row['password_salt'])
            if pass_hash == row['password_hash']:
                if row['request_count'] == 0:
                    res = 'out_of_requests'
                else:
                    res = 'ok'
            else:
                res = 'auth_failed'
        cur.close()
        return res

    # ToDo: remove this
    def check_authorization(self, user, password):
        """Returns True, if password is correct, False otherwise.
        Returns None, if such user is not found in the DB."""
        res = ''
        cur = self.dbconn.cursor(pymysql.cursors.DictCursor)
        sql = """SELECT password, request_count FROM accounts
            WHERE username = '%(username)s'""" % {'username': user}
        cur.execute(sql)
        row = cur.fetchone()
        if row is None:
            res = 'unknown_login'
        else:
            if password == row['password']:
                if row['request_count'] == 0:
                    res = 'out_of_requests'
                else:
                    res = 'ok'
            else:
                res = 'auth_failed'
        cur.close()
        return res

from lxml import etree
import pymysql
import gnm


class AddressOKInitializer:
    """Класс для инициализации БД.

    Создаёт таблицы в БД, заполняет индексы, наименования адресных
    объектов и т.д..
    """

    def __init__(self, dbconn, version_num):
        self.dbconn = dbconn
        # Номер версии БД (при каждом обновлении увеличивается на 1)
        self.version = version_num
        # Суффикс для названий таблиц
        self.version_suffix = '_v'+str(version_num)
    
    def create_tables(self):
        """Создаёт таблицы в БД."""

        cur = self.dbconn.cursor()

        # Таблица, содержащая адресные объекты
        cur.execute("DROP TABLE IF EXISTS addrobj"+self.version_suffix)
        sql = """CREATE TABLE IF NOT EXISTS addrobj%(version_suffix)s (
                id BIGINT NOT NULL AUTO_INCREMENT,

                parentid BIGINT DEFAULT 0,
                zipid INTEGER DEFAULT 0,
                socrcode INTEGER(5) DEFAULT 0,
                displayname VARCHAR(200) DEFAULT '',
                aoguid VARCHAR(36),
                formalname VARCHAR(120),
                offname VARCHAR(120),
                postalcode VARCHAR(6),
                shortname VARCHAR(10),
                aolevel INTEGER(10),
                parentguid VARCHAR(36),
                regioncode VARCHAR(2),

                PRIMARY KEY(id),
                INDEX(parentid),
                INDEX(zipid),
                INDEX(socrcode),
                KEY(aoguid),
                INDEX(postalcode),
                KEY(shortname),
                KEY(aolevel),
                KEY(parentguid)
            );""" % {'version_suffix': self.version_suffix}
        cur.execute(sql)
        
        # Таблица, содержащая сокращения
        cur.execute("DROP TABLE IF EXISTS socrbase"+self.version_suffix)
        sql = """CREATE TABLE IF NOT EXISTS socrbase%(version_suffix)s (
                id BIGINT NOT NULL AUTO_INCREMENT,

                code INTEGER(5) DEFAULT 0,
                level INTEGER(10),
                name VARCHAR(50) DEFAULT '',
                displayname VARCHAR(20) DEFAULT '',
                scname VARCHAR(10),
                socrname VARCHAR(50),
                kod_t_st VARCHAR(4),

                PRIMARY KEY(id),
                INDEX(code),
                INDEX(level),
                INDEX(scname),
                INDEX(socrname),
                KEY(kod_t_st)
            );""" % {'version_suffix': self.version_suffix}
        cur.execute(sql)
        
        # Таблица со списком почтовых индексов
        cur.execute("DROP TABLE IF EXISTS zipcodes"+self.version_suffix)
        sql = """CREATE TABLE IF NOT EXISTS zipcodes%(version_suffix)s (
                id INTEGER NOT NULL AUTO_INCREMENT,

                zip VARCHAR(6),

                PRIMARY KEY(id),
                INDEX(zip)
            );""" % {'version_suffix': self.version_suffix}
        cur.execute(sql)
        
        # Таблица соответствия почтовых индексов адресным объектам
        cur.execute("DROP TABLE IF EXISTS ziplinks"+self.version_suffix)
        sql = """CREATE TABLE IF NOT EXISTS ziplinks%(version_suffix)s (
                id INTEGER NOT NULL AUTO_INCREMENT,

                zipid INTEGER,
                aoid BIGINT,

                PRIMARY KEY(id),
                INDEX(zipid),
                INDEX(aoid)
            );""" % {'version_suffix': self.version_suffix}
        cur.execute(sql)
        
        cur.close()

    def _clear_address_objects(self):
        cur = self.dbconn.cursor()
        cur.execute('TRUNCATE TABLE addrobj'+self.version_suffix)
        cur.close()

    def _clear_socr(self):
        cur = self.dbconn.cursor()
        cur.execute('TRUNCATE TABLE socrbase'+self.version_suffix)
        cur.close()

    def load_address_objects(self, fname):
        """Загружает адресные объекты из файла в таблицу ADDOBJ."""
        self._clear_address_objects()

        cur = self.dbconn.cursor()

        cnt = 0

        for event, element in etree.iterparse(fname, events=('end',)):
            if element.get('LIVESTATUS') == '1' and element.get('ACTSTATUS') == '1':
                sql = """INSERT INTO addrobj%(version_suffix)s (aoguid, formalname, offname,
                        postalcode, shortname,
                        aolevel, parentguid, regioncode)
                    VALUES ('%(AOGUID)s', '%(FORMALNAME)s', '%(OFFNAME)s',
                        '%(POSTALCODE)s', '%(SHORTNAME)s',
                        %(AOLEVEL)s, '%(PARENTGUID)s', '%(REGIONCODE)s')""" % {
                            'version_suffix': self.version_suffix,
                            'AOGUID': element.get('AOGUID'),
                            'FORMALNAME': element.get('FORMALNAME').replace("'", "''")\
                                if element.get('FORMALNAME') is not None else None,
                            'OFFNAME': element.get('OFFNAME').replace("'", "''")\
                                if element.get('OFFNAME') is not None else None,
                            'POSTALCODE': element.get('POSTALCODE'),
                            'SHORTNAME': element.get('SHORTNAME'),
                            'AOLEVEL': element.get('AOLEVEL'),
                            'PARENTGUID': element.get('PARENTGUID'),
                            'REGIONCODE': element.get('REGIONCODE'),
                        }
                cur.execute(sql)

            while element.getprevious() is not None:
                del element.getparent()[0]

            element.clear()

            cnt += 1
            if cnt % 1000 == 0:
                self.dbconn.commit()
                print("Loading data into ADDROBJ.", cnt)

        if cnt % 1000 != 0:
            print("Loading data into ADDROBJ.", cnt)
        
        self.dbconn.commit()

        cur.close()

    def load_socr(self, fname):
        """Загружает сокращения из файла в таблицу SOCRBASE."""
        self._clear_socr()

        cur = self.dbconn.cursor()

        cnt = 0

        for event, element in etree.iterparse(fname, events=('end',)):
            if element.get('SCNAME') is not None:
                sql = """INSERT INTO socrbase%(version_suffix)s (level, scname, socrname, kod_t_st)
                    VALUES (%(LEVEL)s, '%(SCNAME)s', '%(SOCRNAME)s', '%(KOD_T_ST)s')""" % {
                        'version_suffix': self.version_suffix,
                        'LEVEL': element.get('LEVEL'),
                        'SCNAME': element.get('SCNAME'),
                        'SOCRNAME': element.get('SOCRNAME'),
                        'KOD_T_ST': element.get('KOD_T_ST'),
                }
                cur.execute(sql)

            while element.getprevious() is not None:
                del element.getparent()[0]

            element.clear()

            cnt += 1
            if cnt % 1000 == 0:
                self.dbconn.commit()
                print("Loading data into SOCRBASE.", cnt)

        if cnt % 1000 != 0:
            print("Loading data into SOCRBASE.", cnt)

        self.dbconn.commit()
        cur.close()

    def fill_zip_codes(self):
        """Заполняет таблицу ZIPCODES."""
        cur = self.dbconn.cursor(pymysql.cursors.DictCursor)
        cur2 = self.dbconn.cursor()

        cur.execute('TRUNCATE TABLE zipcodes'+self.version_suffix);
        self.dbconn.commit()

        cur.execute("""SELECT DISTINCT
                postalcode
            FROM addrobj%(version_suffix)s
            WHERE
                postalcode is not null and postalcode != 'None'
            ORDER BY postalcode""" % {'version_suffix': self.version_suffix})
        cnt = 0
        for row in cur.fetchall():
            sql = """INSERT INTO zipcodes%(version_suffix)s (zip)
                VALUES ('%(postalcode)s')""" % {
                    'version_suffix': self.version_suffix,
                    'postalcode': row['postalcode']
                }
            cur2.execute(sql)

            cnt += 1
            if cnt % 1000 == 0:
                print("Filling ZIPCODES table.", cnt)
                self.dbconn.commit()

        if cnt % 1000 != 0:
            print("Filling ZIPCODES table.", cnt)

        cur2.close()
        cur.close()
        self.dbconn.commit()

    def _get_parentguids(self, aoguid):
        """Возвращает список GUID'ов для адресного объекта."""
        if aoguid == 'None':
            return []
        ret = []

        cur = self.dbconn.cursor(pymysql.cursors.DictCursor)
        sql = """SELECT parentguid FROM addrobj%(version_suffix)s
            WHERE aoguid = '%(aoguid)s'""" % {
                'version_suffix': self.version_suffix,
                'aoguid': aoguid
            }
        cur.execute(sql)
        row = cur.fetchone()
        cur.close()

        if row['parentguid'] is not None:
            ret.append(row['parentguid'])
            ret.extend(self._get_parentguids(row['parentguid']))

        return ret

    def _fill_zip_links(self, zipcode):
        """Заполняет связи для почтового индекса."""

        cur = self.dbconn.cursor(pymysql.cursors.DictCursor)

        # Список GUID'ов адресных объектов с данным почтовым индексом
        guids = []

        sql = """SELECT
            ao.aolevel,
            ao.aoguid,
            ao.parentguid
        FROM addrobj%(version_suffix)s ao
        WHERE
            postalcode = '%(zipcode)s'
            """ % {
                'version_suffix': self.version_suffix,
                'zipcode': zipcode
            }
        cur.execute(sql)
        for row in cur:
            guids.append(row['aoguid'])
            # Получаем GUID'ы родительских адресных объектов
            guids.extend(self._get_parentguids(row['aoguid']))

        # Убираем дублирующиеся элементы списка
        guids = list(set(guids))

        sql = """INSERT INTO ziplinks%(version_suffix)s (zipid, aoid)
            SELECT
                (SELECT id FROM zipcodes%(version_suffix)s WHERE zip = '%(zipcode)s' LIMIT 1),
                ao.id
            FROM addrobj%(version_suffix)s ao
            WHERE
                ao.aoguid in (%(guids)s)""" %\
                    {
                        'version_suffix': self.version_suffix,
                        'zipcode': zipcode,
                        'guids': ', '.join([("'%s'" % guid) for guid in guids])
                    }
        cur.execute(sql)
        cur.close()

    def fill_zip_links(self):
        """Заполняем соответствие почтовых индексов адресным объектам."""
        cur = self.dbconn.cursor(pymysql.cursors.DictCursor)

        cur.execute('TRUNCATE TABLE ziplinks'+self.version_suffix);
        self.dbconn.commit()

        # Получаем кол-во почтовых индексов (для счётчика)
        sql = """SELECT count(*) cnt FROM zipcodes%(version_suffix)s""" % {
            'version_suffix': self.version_suffix
        }
        cur.execute(sql)
        cnt_all = cur.fetchone()['cnt']
        cnt = 0

        sql = """SELECT * FROM zipcodes%(version_suffix)s""" % {
            'version_suffix': self.version_suffix
        }
        cur.execute(sql)
        for row in cur:
            self._fill_zip_links(row['zip'])

            cnt += 1
            if cnt % 100 == 0:
                print("Filling ZIPLINKS table. %s / %s" % (cnt, cnt_all))
                self.dbconn.commit()

        if cnt % 100 != 0:
            print("Filling ZIPLINKS table. %s / %s" % (cnt, cnt_all))

        self.dbconn.commit()

        cur.close()

    def fill_socr_codes(self):
        """Заполняет целочисленные коды в таблице SOCRBASE."""

        cur1 = self.dbconn.cursor(pymysql.cursors.DictCursor)
        cur2 = self.dbconn.cursor(pymysql.cursors.DictCursor)

        sql = """SELECT * FROM socrbase%(version_suffix)s""" % {
            'version_suffix': self.version_suffix
        }
        cur1.execute(sql)
        for row in cur1:
            if row['kod_t_st'] is not None:
                sql = """UPDATE socrbase%(version_suffix)s
                    SET
                        code = %(code)i
                    WHERE
                        id = %(id)i""" % \
                    {
                        'version_suffix': self.version_suffix,
                        'id': row['id'],
                        'code': int(row['kod_t_st'])
                    }
                cur2.execute(sql)

        self.dbconn.commit()
        
        cur2.close()
        cur1.close()

    def fill_socr_names(self):
        """Заполняет поле NAME в таблице SOCRBASE (заполняет его
        в нижнем регистре)."""
        cur1 = self.dbconn.cursor(pymysql.cursors.DictCursor)
        cur2 = self.dbconn.cursor(pymysql.cursors.DictCursor)

        sql = """SELECT * FROM socrbase%(version_suffix)s""" % {
            'version_suffix': self.version_suffix
        }
        cur1.execute(sql)
        for row in cur1:
            sql = """UPDATE socrbase%(version_suffix)s
                SET
                    name = '%(name)s'
                WHERE
                    id = %(id)i""" % \
                {
                    'version_suffix': self.version_suffix,
                    'id': row['id'],
                    'name': row['socrname'].lower()
                }
            cur2.execute(sql)

        self.dbconn.commit()

        cur2.close()
        cur1.close()

    def fill_addrobj_socr(self, step=1000):
        """Заполняет поле SOCRCODE в таблице ADDROBJ."""
        cur1 = self.dbconn.cursor(pymysql.cursors.DictCursor)
        cur2 = self.dbconn.cursor(pymysql.cursors.DictCursor)

        where = "ao.aolevel = 1 and livestatus = 1"
        where = "ao.aolevel not in (90, 91)"

        # Счётчик
        print('Counting...')
        sql = """SELECT
                count(*) cnt
            FROM addrobj%(version_suffix)s ao
            INNER JOIN socrbase%(version_suffix)s s ON s.level = ao.aolevel and s.scname = ao.shortname
            WHERE %(where)s""" % {
                'version_suffix': self.version_suffix,
                'where': where
            }
        cur1.execute(sql)
        cnt_all = cur1.fetchone()['cnt']
        cnt = 0
        print('Total %i' % cnt_all)

        # Обработка
        sql = """SELECT
                ao.id aoid,
                s.code socrcode
            FROM addrobj%(version_suffix)s ao
            INNER JOIN socrbase%(version_suffix)s s ON s.level = ao.aolevel and s.scname = ao.shortname
            WHERE %(where)s""" % {
                'version_suffix': self.version_suffix,
                'where': where
            }
        cur1.execute(sql)
        for row in cur1:
            sql = """UPDATE addrobj%(version_suffix)s SET socrcode = %(socrcode)i WHERE id = %(aoid)i""" % {
                'version_suffix': self.version_suffix,
                'aoid': row['aoid'],
                'socrcode': row['socrcode'],
            }
            cur2.execute(sql)

            cnt += 1
            if cnt % step == 0:
                print('Filling SOCRCODE field in ADDROBJ table. %s / %s' % (cnt, cnt_all))
                self.dbconn.commit()

        if cnt % step != 0:
            print('Filling SOCRCODE field in ADDROBJ table. %s / %s' % (cnt, cnt_all))
            self.dbconn.commit()

        cur2.close()
        cur1.close()

    def fill_socr_diplaynames(self):
        """Заполняет поле DISPLAYNAME в таблице SOCRBASE."""
        cur1 = self.dbconn.cursor(pymysql.cursors.DictCursor)
        cur2 = self.dbconn.cursor(pymysql.cursors.DictCursor)

        # Свойство 'type' обозначает тип сокращения:
        # 'dot' -- пишется с точкой в конце ("г.", "ул." и т.д.)
        # 'upper' -- пишется большими буквами ("СНТ", "ДНП" и т.д.)
        dn = {
            102: {'name': 'АО', 'scname': 'Аобл'},
            103: {'type': 'dot', 'scname': 'г'},
            105: {'type': 'dot', 'scname': 'обл'},
            106: {'name': 'респ.', 'scname': 'Респ'},
            306: {'type': 'dot', 'scname': 'п'},
            303: {'type': 'dot', 'scname': 'тер'},
            302: {'type': 'dot', 'scname': 'у'},
            401: {'type': 'dot', 'scname': 'г'},
            405: {'type': 'upper', 'scname': 'дп'},
            404: {'type': 'upper', 'scname': 'кп'},
            417: {'type': 'dot', 'scname': 'п'},
            412: {'type': 'dot', 'scname': 'тер'},
            502: {'type': 'dot', 'scname': 'тер'},
            604: {'type': 'dot', 'scname': 'высел'},
            605: {'type': 'dot', 'scname': 'г'},
            606: {'type': 'dot', 'scname': 'д'},
            617: {'type': 'dot', 'scname': 'м'},
            621: {'type': 'dot', 'scname': 'п'},
            630: {'type': 'dot', 'scname': 'с'},
            631: {'type': 'dot', 'scname': 'сл'},
            641: {'type': 'upper', 'scname': 'снт'},
            632: {'type': 'dot', 'scname': 'ст'},
            637: {'type': 'dot', 'scname': 'тер'},
            634: {'type': 'dot', 'scname': 'у'},
            635: {'type': 'dot', 'scname': 'х'},
            #734: {'type': 'dot', 'scname': 'высел'},
            763: {'type': 'upper', 'scname': 'гск'},
            736: {'type': 'dot', 'scname': 'д'},
            787: {'type': 'upper', 'scname': 'днп'},
            704: {'type': 'dot', 'scname': 'дор'},
            744: {'type': 'dot', 'scname': 'м'},
            711: {'type': 'dot', 'scname': 'наб'},
            714: {'type': 'dot', 'scname': 'пер'},
            9114: {'type': 'dot', 'scname': 'пер'},
            716: {'type': 'dot', 'scname': 'пл'},
            747: {'type': 'dot', 'scname': 'платф'},
            755: {'type': 'dot', 'scname': 'с'},
            756: {'type': 'dot', 'scname': 'сл'},
            757: {'type': 'dot', 'scname': 'ст'},
            725: {'type': 'dot', 'scname': 'стр'},
            726: {'type': 'dot', 'scname': 'тер'},
            728: {'type': 'dot', 'scname': 'туп'},
            729: {'type': 'dot', 'scname': 'ул'},
            9129: {'type': 'dot', 'scname': 'ул'},
            758: {'type': 'dot', 'scname': 'х'},
            731: {'type': 'dot', 'scname': 'ш'},
        }

        sql = """SELECT * FROM socrbase%(version_suffix)s""" % {
            'version_suffix': self.version_suffix
        }
        cur1.execute(sql)
        for row in cur1:
            row['displayname'] = row['scname']
            if row['code'] in dn.keys():
                if row['scname'] != dn[row['code']]['scname']:
                    print(row['code'])
                    print(row['scname'].encode('utf-8'))
                    print(dn[row['code']]['scname'].encode('utf-8'))
                assert row['scname'] == dn[row['code']]['scname']

                if 'type' in dn[row['code']].keys():
                    socrtype = dn[row['code']]['type']
                    if socrtype == 'dot':
                        row['displayname'] = row['scname']+'.'
                    elif socrtype == 'upper':
                        row['displayname'] = row['scname'].upper()
                if 'name' in dn[row['code']].keys():
                    row['displayname'] = dn[row['code']]['name']

            row['version_suffix'] = self.version_suffix
            sql = """UPDATE socrbase%(version_suffix)s SET displayname = '%(displayname)s'
                WHERE id = %(id)i""" % row
            cur2.execute(sql)

        self.dbconn.commit()

        cur2.close()
        cur1.close()


    def fill_good_names_old(self):
        """Заполняет поле DISPLAYNAME в таблице ADDROBJ."""
        cur1 = self.dbconn.cursor(pymysql.cursors.DictCursor)
        cur2 = self.dbconn.cursor(pymysql.cursors.DictCursor)

        names_maker = gnm.GoodNamesMaker()

        sql = """SELECT count(*) cnt FROM addrobj%(version_suffix)s ao
            INNER JOIN socrbase%(version_suffix)s s ON s.code = ao.socrcode""" % {
                'version_suffix': self.version_suffix
            }
        print('Counting...')
        cur1.execute(sql)
        cnt_all = cur1.fetchone()['cnt']
        print('Total: %s' % cnt_all)

        sql = """SELECT
                ao.id,
                ao.formalname,
                s.socrname,
                s.code s_code,
                s.scname,
                s.displayname s_displayname,
                ao.aolevel,
                ao.regioncode
            FROM addrobj%(version_suffix)s ao
            INNER JOIN socrbase%(version_suffix)s s ON s.code = ao.socrcode
            """ % {
                'version_suffix': self.version_suffix
            }
        print('Selecting...')
        cur1.execute(sql)
        cnt = 0
        for row in cur1:
            good_name = names_maker.make_good_name(row)

            sql = """UPDATE addrobj%(version_suffix)s SET displayname = '%(good_name)s'
                WHERE id = %(ao_id)s""" % {
                    'version_suffix': self.version_suffix,
                    'good_name': good_name,
                    'ao_id': row['id'],
                }
            cur2.execute(sql)

            cnt += 1
            if cnt % 100 == 0:
                print('Filling DISPLAYNAME field in ADDROBJ table. %s / %s' % (cnt, cnt_all))
                self.dbconn.commit()

        if cnt % 100 != 0:
            print('Filling DISPLAYNAME field in ADDROBJ table. %s / %s' % (cnt, cnt_all))
        self.dbconn.commit()

        cur2.close()
        cur1.close()


    def fill_good_names(self):
        """Заполняет поле DISPLAYNAME в таблице ADDROBJ."""
        cur1 = self.dbconn.cursor(pymysql.cursors.DictCursor)
        cur2 = self.dbconn.cursor(pymysql.cursors.DictCursor)


        # ToDo: remove this.
        if False:
            sql = """SELECT * FROM socrbase%(version_suffix)s""" % {
                'version_suffix': self.version_suffix
            }
            cur1.execute(sql)
            for row in cur1:
                print(row['code'])
                print(row['level'])
            return


        names_maker = gnm.GoodNamesMaker()

        sql = """SELECT count(*) cnt FROM addrobj%(version_suffix)s ao
            INNER JOIN socrbase%(version_suffix)s s ON s.code = ao.socrcode""" % {
                'version_suffix': self.version_suffix
            }
        print('Counting...')
        cur1.execute(sql)
        cnt_all = cur1.fetchone()['cnt']
        print('Total: %s' % cnt_all)

        # ToDo: remove commented-out lines
        sql = """SELECT
                ao.id,
                # ao.formalname,
                # ao.offname,
                # ao.socrname,
                ao.socrcode
                # ao.aolevel,
                # ao.regioncode
            FROM addrobj%(version_suffix)s ao
            -- INNER JOIN socrbase%(version_suffix)s s ON s.code = ao.socrcode
            WHERE ao.socrcode != 0
            -- LIMIT 20
            """ % {
                'version_suffix': self.version_suffix
            }
        print('Selecting...')
        cur1.execute(sql)
        cnt = 0
        for row in cur1:
            sql = """SELECT
                    id,
                    formalname,
                    socrcode,
                    aolevel,
                    regioncode
                FROM addrobj%(version_suffix)s ao
                WHERE ao.id = %(id)s""" % {
                    'id': row['id'],
                    'version_suffix': self.version_suffix,
                }
            cur2.execute(sql)
            row2 = cur2.fetchone()

            sql = """SELECT
                    s.socrname,
                    s.code s_code,
                    s.scname,
                    s.displayname s_displayname
                FROM socrbase%(version_suffix)s s
                WHERE s.code = %(socrcode)s""" % {
                    'socrcode': row2['socrcode'],
                    'version_suffix': self.version_suffix,
                }
            cur2.execute(sql)
            row_socr = cur2.fetchone()

            row2.update(row_socr)

            good_name = names_maker.make_good_name(row2)

            sql = """UPDATE addrobj%(version_suffix)s SET displayname = '%(good_name)s'
                WHERE id = %(ao_id)s""" % {
                    'version_suffix': self.version_suffix,
                    'good_name': good_name,
                    'ao_id': row2['id'],
                }
            cur2.execute(sql)

            cnt += 1
            if cnt % 100 == 0:
                print('Filling DISPLAYNAME field in ADDROBJ table. %s / %s' % (cnt, cnt_all))
                self.dbconn.commit()

        if cnt % 100 != 0:
            print('Filling DISPLAYNAME field in ADDROBJ table. %s / %s' % (cnt, cnt_all))
        self.dbconn.commit()

        cur2.close()
        cur1.close()

    # ToDo: remove this.
    def fill_parent_ids_old(self):
        cur1 = self.dbconn.cursor(pymysql.cursors.DictCursor)
        cur2 = self.dbconn.cursor(pymysql.cursors.DictCursor)

        # Counting rows
        sql = """SELECT count(*) cnt FROM addrobj%(version_suffix)s""" % {
            'version_suffix': self.version_suffix
        }
        cur1.execute(sql)
        cnt_all = cur1.fetchone()['cnt']
        print('Total: %i' % cnt_all)

        cnt = 0

        sql = """SELECT
                ao.id ao_id,
                ao.parentguid,
                ao2.aoguid,
                ao2.id ao2_id
            FROM addrobj%(version_suffix)s ao
            LEFT JOIN addrobj%(version_suffix)s ao2 ON ao.parentguid = ao2.aoguid
            -- LIMIT 100
            """ % {
                'version_suffix': self.version_suffix
            }
        cur1.close()
        cur1 = self.dbconn.cursor(pymysql.cursors.DictCursor)
        cur1.execute(sql)
        for row in cur1:
            print(row)
            # if row['ao2_id'] is None:
            #     row['ao2_id'] = 0
            # row['version_suffix'] = self.version_suffix
            # sql = """UPDATE addrobj%(version_suffix)s SET parentid = %(ao2_id)s
            #     WHERE id = %(ao_id)s""" % row
            # cur2.execute(sql)

            # cnt += 1
            # if cnt % 100 == 0:
            #     print('%s / %s' % (cnt, cnt_all))
            #     self.dbconn.commit()

        if cnt % 100 != 0:
            print('%s / %s' % (cnt, cnt_all))
            self.dbconn.commit()
        self.dbconn.commit()

        cur2.close()
        cur1.close()


    def fill_parent_ids(self):
        """Заполняет поле PARENTID в таблице ADDROBJ."""
        cur1 = self.dbconn.cursor(pymysql.cursors.DictCursor)
        cur2 = self.dbconn.cursor(pymysql.cursors.DictCursor)

        # Счётчик
        sql = """SELECT count(*) cnt FROM addrobj%(version_suffix)s""" % {
            'version_suffix': self.version_suffix
        }
        cur1.execute(sql)
        cnt_all = cur1.fetchone()['cnt']
        print('Total: %i' % cnt_all)

        cnt = 0

        sql = """SELECT
                ao.id ao_id,
                ao.parentguid
            FROM addrobj%(version_suffix)s ao
            """ % {
                'version_suffix': self.version_suffix
            }
        cur1.close()
        cur1 = self.dbconn.cursor(pymysql.cursors.DictCursor)
        cur1.execute(sql)
        for row in cur1:
            row['version_suffix'] = self.version_suffix

            sql = """SELECT id FROM addrobj%(version_suffix)s
                WHERE aoguid = '%(parentguid)s' LIMIT 1""" % row
            cur2.execute(sql)
            res = cur2.fetchone()
            parent_id = res['id'] if res is not None else 0

            row['parent_id'] = parent_id

            sql = """UPDATE addrobj%(version_suffix)s
                SET parentid = %(parent_id)s
                WHERE id = %(ao_id)s""" % row
            cur2.execute(sql)

            cnt += 1
            if cnt % 100 == 0:
                print('Filling PARENTID field in ADDROBJ table. %s / %s' % (cnt, cnt_all))
                self.dbconn.commit()

        if cnt % 100 != 0:
            print('Filling PARENTID field in ADDROBJ table. %s / %s' % (cnt, cnt_all))
            self.dbconn.commit()
        self.dbconn.commit()

        cur2.close()
        cur1.close()

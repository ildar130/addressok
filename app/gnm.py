import re

class GoodNamesMaker:
    """Класс для заполнения наименований адресных объектов в том виде,
    в котором они будут отображаться в форме заполнения алдреса."""
    
    def __init__(self):
        # Regex patterns
        self.rep_male_singular_adj = re.compile('^(?P<name>([^\s]+ский)|([^\s]+ный)|([^\s]+овый))\s*$')
        self.rep_male_singular_named_by = re.compile('^\s*(и|И)м\s+(?P<name>.*)\s*$')
        self.rep_male_singular_num = re.compile('^(?P<first>(.*\s)|)(?P<num>\d+\-й)(?P<last>(\s.*)|)$')
        self.rep_female_singular_adj = re.compile('^(?P<name>([^\s]+ская)|([^\s]+ная))\s*$')
        self.rep_female_singular_named_by = re.compile('^\s*(и|И)м\s+(?P<name>.*)\s*$')
        self.rep_female_singular_num = re.compile('^(?P<first>(.*\s)|)(?P<num>\d+\-я)(?P<last>(\s.*)|)$')
        self.rep_square_01 = re.compile('^\s*(?P<name>.*)\s+площадь\s*$')

    def _default_good_name(self, row):
        """Возвращает отображаемое имя по умолчанию."""
        return '%s %s' % (row['s_displayname'], row['formalname'])

    def _good_name_male_singular(self, row):
        """Возвращает отображаемое имя для наименований мужского рода
        единственного числа."""
        good_name = self._default_good_name(row)

        # *ский проезд, *ный проезд
        male_singular_adj_match = None
        # Напр., Им 50-летия Октября
        male_singular_named_by_match = None
        # Проезд с номером
        male_singular_num_match = None

        male_singular_adj_match = self.rep_male_singular_adj.match(row['formalname'])
        if not male_singular_adj_match:
            male_singular_named_by_match = self.rep_male_singular_named_by.match(row['formalname'])
            if not male_singular_named_by_match:
                male_singular_num_match = self.rep_male_singular_num.match(row['formalname'])

        if male_singular_adj_match:
            name = male_singular_adj_match.group('name')
            good_name = '%s %s' % (name, row['s_displayname'])
        elif male_singular_named_by_match:
            name = male_singular_named_by_match.group('name')
            good_name = '%s им. %s' % (row['s_displayname'], name)
        elif male_singular_num_match:
            first = male_singular_num_match.group('first').strip()
            num = male_singular_num_match.group('num')
            last = male_singular_num_match.group('last').strip()

            # Напр., 2-й Степной проезд
            if first == '' and last != '':
                # good_name = '%s %s' % (row['s_displayname'], row['formalname'])
                good_name = '%s %s %s' % (num, last, row['s_displayname'])
            # Напр., проезд Строителей 2-й
            elif first != '' and last == '':
                good_name = '%s %s %s' % (num, row['s_displayname'], first)
            # Напр., 3-я линия
            elif first == '' and last == '':
                good_name = '%s %s' % (num, row['s_displayname'])

        return good_name
        
    def _good_name_female_singular(self, row, is_square=False):
        """Возвращает отображаемое имя для наименований женского рода
        единственного числа.

        Аргументы:
            is_square (bool): True, если это площадь.
        """
        good_name = self._default_good_name(row)

        # *ская площадь, *ная площадь
        female_singular_adj_match = None
        # Напр., Им 50-летия Октября
        female_singular_named_by_match = None
        female_singular_num_match = None
        # Напр., пл. Центральная площадь
        square_01_match = None

        female_singular_adj_match = self.rep_female_singular_adj.match(row['formalname'])
        if not female_singular_adj_match:
            female_singular_named_by_match = self.rep_female_singular_named_by.match(row['formalname'])
            if not female_singular_named_by_match:
                female_singular_num_match = self.rep_female_singular_num.match(row['formalname'])
                if not female_singular_num_match and is_square:
                    square_01_match = self.rep_square_01.match(row['formalname'])

        if female_singular_adj_match:
            name = female_singular_adj_match.group('name')
            good_name = '%s %s' % (name, row['s_displayname'])
        elif female_singular_named_by_match:
            name = female_singular_named_by_match.group('name')
            good_name = '%s им. %s' % (row['s_displayname'], name)
        elif female_singular_num_match:
            first = female_singular_num_match.group('first').strip()
            num = female_singular_num_match.group('num')
            last = female_singular_num_match.group('last').strip()

            # Напр., 2-я линия Южная поляна, 2-я линия Строителей
            if first == '' and last != '':
                # good_name = '%s %s' % (row['s_displayname'], row['formalname'])
                good_name = '%s %s %s' % (num, row['s_displayname'], last)
                # good_name = '%s %s %s' % (num, last, row['s_displayname'])
            # Напр., Южная поляна 2-я линия
            elif first != '' and last == '':
                good_name = '%s %s' % (row['formalname'], row['s_displayname'])
            # Напр., 3-я линия
            elif first == '' and last == '':
                good_name = '%s %s' % (row['formalname'], row['s_displayname'])
        elif square_01_match:
            name = square_01_match.group('name')
            good_name = '%s %s' % (name, row['s_displayname'])

        return good_name

    def make_good_name(self, row):
        """Получает запись из БД и возвращает для неё отображаемое имя."""
        good_name = '%s %s' % (row['s_displayname'], row['formalname'])

        # автономный округ
        if row['s_code'] in (101, 201, 305):
            assert row['scname'] == 'АО'
            good_name = '%s %s' % (row['formalname'], row['s_displayname'])
        # город
        elif row['s_code'] in (103, 401, 605):
            assert row['scname'] == 'г'
            good_name = '%s %s' % (row['s_displayname'], row['formalname'])
        # first level objects
        elif row['aolevel'] == 1:
            # Республика Чувашия
            if row['regioncode'] == '21':
                good_name = 'Чувашская Республика'
            # край
            elif row['s_code'] == 104:
                assert row['scname'] == 'край'
                good_name = '%s %s' % (row['formalname'], row['s_displayname'])
            # область
            elif row['s_code'] == 105:
                assert row['scname'] == 'обл'
                good_name = '%s %s' % (row['formalname'], row['s_displayname'])
            # # город федерального значения
            # elif row['regioncode'] in ('77', '78', '92', '99'):
            #     good_name = '%s %s' % (row['s_displayname'], row['formalname'])
            # автономная область
            elif row['s_code'] == 102:
                assert row['scname'] == 'Аобл'
                good_name = '%s %s' % (row['formalname'], row['s_displayname'])
            # Ханты-Мансийский Автономный округ - Югра
            elif row['regioncode'] == '86':
                good_name = 'Ханты-Мансийский АО'
            # Напр., Республика Татарстан
            elif row['regioncode'] in ('01', '02', '03', '04', '05', '06', '08',
                '10', '11', '12', '13', '14', '15', '16', '17', '19', '91'):
                good_name = '%s %s' % (row['socrname'], row['formalname'])
            # Напр., Чеченская Республика
            elif row['regioncode'] in ('07', '09', '18', '20'):
                good_name = '%s %s' % (row['formalname'], row['socrname'])
        # район
        elif row['s_code'] in (301, 503):
            assert row['scname'] == 'р-н'
            good_name = '%s %s' % (row['formalname'], row['s_displayname'])
        # квартал
        elif row['s_code'] in (639, 707, 9107):
            assert row['scname'] == 'кв-л'
            good_name = self._good_name_male_singular(row)
        # проспект
        elif row['s_code'] in (719, 9119):
            assert row['scname'] == 'пр-кт'
            good_name = self._good_name_male_singular(row)
        # проезд
        elif row['s_code'] in (718, 9118):
            assert row['scname'] == 'проезд'
            good_name = self._good_name_male_singular(row)
        # переулок
        elif row['s_code'] in (714, 9114) and True:
            assert row['scname'] == 'пер'
            good_name = self._good_name_male_singular(row)
        # линия
        elif row['s_code'] in (710, 9110):
            assert row['scname'] == 'линия'
            good_name = self._good_name_female_singular(row)
        # площадь
        elif row['s_code'] in (716, 9116):
            assert row['scname'] == 'пл'
            good_name = self._good_name_female_singular(row, is_square=True)
        # Улица
        elif row['s_code'] in (729, 9129) and True:
            assert row['scname'] == 'ул'
            good_name = '%s %s' % (row['s_displayname'], row['formalname'])

        return good_name
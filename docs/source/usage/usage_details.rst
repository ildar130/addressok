.. _connect-to-site:

Подключение к сайту
===============================================================================

На этой странице описан процесс подключения сервиса к сайту на PHP
или Python после того, как вы запустили сервер AddressOK.

Требования
-------------------------------------------------------------------------------

Для работы jQuery-плагина AddressOK требуются библиотеки jQuery и jQuery UI
с компонентом Autocomplete.

Подключение
-------------------------------------------------------------------------------

Лицевая часть сайта (front end)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Библиотеки и jQuery-плагин
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

На странице с адресной формой необходимо подключить библиотеки jQuery и
jQuery UI

.. code-block:: html
    
    <link href="/путь/к/jquery-ui.min.css" rel="stylesheet">
    <script src="/путь/к/jquery-2.2.1.min.js"></script>
    <script src="/путь/к/jquery-ui.min.js"></script>

а также плагин AddressOK

.. code-block:: html
    
    <script src="/путь/к/addressok.js"></script>

Версия Вашей библиотеки jQuery может отличаться. Версия 2.2.1 приведена лишь в качестве примера.

HTML-форма
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

Форма для ввода адреса должна обязательно иметь текстовые поля для ввода
следующих элементов адреса: почтовый индекс, регион (область, республика
и т.д.), район, населённый пункт (город, посёлок, село, деревня и т.д.),
улица (переулок, проспект и т.д.).

Все такие поля должны быть элементами input с типом text и иметь атрибут data-addressok-field со следующими значениями:
data-addressok-field="zip" — для поля "Почтовый индекс";
data-addressok-field="region" — для поля "Регион";
data-addressok-field="district" — для поля "Район";
data-addressok-field="place" — для поля "Населённый пункт";
data-addressok-field="street" — для поля "Улица".

Например, поле для ввода почтового индекса может выглядеть так:

.. code-block:: html
    
    <input type="text" data-addressok-field="zip">

Пример формы ввода адреса:

.. code-block:: html
    
    <!-- Форма для ввода адреса -->
    <form id="addr_form">
        <div>
            <label for="zip">Почтовый индекс</label>
            <!-- Поле для ввода почтового индекса -->
            <input id="zip" type="text" data-addressok-field="zip">
        </div>
        <div>
            <label for="region">Регион (область, край, республика и т.д.)</label>
            <!-- Поле для ввода региона -->
            <input id="region" type="text" data-addressok-field="region">
        </div>
        <div>
            <label for="district">Район</label>
            <!-- Поле для ввода района -->
            <input id="district" type="text" data-addressok-field="district">
        </div>
        <div>
            <label for="place">Населённый пункт (город, посёлок, село, деревня и т.д.)</label>
            <!-- Поле для ввода населённого пункта -->
            <input id="place" type="text" data-addressok-field="place">
        </div>
        <div>
            <label for="street">Улица, переулок, проспект и т.д.</label>
            <!-- Поле для ввода улицы -->
            <input id="street" type="text" data-addressok-field="street">
        </div>
        <div>
            <label for="house">Дом</label>
            <input id="house" type="text">
        </div>
        <div>
            <button type="submit">OK</button>
        </div>
    </form>

JavaScript
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

Необходимо применить плагин AddressOK к элементу адресной формы:

.. code-block:: javascript

    $('css_селектор_формы').AddressOK('/URL/для/ajax-запросов');
    
Для формы, приведённой в примере выше, применение плагина может выглядеть так:

.. code-block:: javascript

    $('#addr_form').AddressOK('/addr_ajax.php');

где ``/addr_ajax.php`` — адрес страницы для адресных Ajax-запросов на Вашем
сервере.

Пример страницы с адресной формой
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

.. code-block:: html

    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Пример страницы с формой ввода адреса</title>

        <!-- Подключение стилей jQuery UI -->
        <link href="/static/js/jquery-ui/jquery-ui.min.css" rel="stylesheet">

        <!-- Подключение плагинов jQuery и jQuery UI -->
        <script src="/static/js/jquery-2.2.1.min.js"></script>
        <script src="/static/js/jquery-ui/jquery-ui.min.js"></script>
        
        <!-- Подключение плагина AddressOK -->
        <script src="/static/js/addressok.js"></script>
    </head>
    <body>
        
        <!-- Форма ввода адреса -->
        <form id="addr_form">
            <div>
                <label for="zip">Почтовый индекс</label>
                <!-- Поле для ввода почтового индекса -->
                <input id="zip" data-addressok-field="zip" type="text">
            </div>
            <div>
                <label for="region">Регион (область, край, республика и т.д.)</label>
                <!-- Поле для ввода региона -->
                <input id="region" data-addressok-field="region" type="text">
            </div>
            <div>
                <label for="district">Район</label>
                <!-- Поле для ввода района -->
                <input id="district" data-addressok-field="district" type="text">
            </div>
            <div>
                <label for="place">Населённый пункт (город, посёлок, село, деревня и т.д.)</label>
                <!-- Поле для ввода населённого пункта -->
                <input id="place" data-addressok-field="place" type="text">
            </div>
            <div>
                <label for="street">Улица, переулок, проспект и т.д.</label>
                <!-- Поле для ввода улицы -->
                <input id="street" data-addressok-field="street" type="text">
            </div>
            <div>
                <label for="house">Дом</label>
                <input id="house" data-addressok-field="house" type="text">
            </div>
            <div class="line align-right">
                <button type="submit">OK</button>
            </div>
        </form>

        <script>
            // Применяем плагин к форме адреса
            $('#addr_form').AddressOK('/addr_ajax.php');
        </script>

    </body>
    </html>

Серверная часть сайта на PHP (back end)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

В серверной части Вашего сайта должна быть страница для Ajax-запросов, которые
генерирует jQuery-плагин AddressOK. На этой странице должен быть подключен
файл addressok.php.

Эта страница должна получать POST-запрос, передавать его в функцию
AddressOK_GetData() (расположенную в подключенном файле addressok.php) и
возвращать результат работы этой функции:

.. code-block:: php

    <?php

    require_once('addressok.php');

    if ($_SERVER['REQUEST_METHOD'] == 'POST') {
        // Отдаём в ответ на запрос адресные данные
        echo AddressOK_GetData($_POST);
    }

    ?>

Серверная часть сайта на Python (back end) на примере Flask
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

На Вашем сайте должен быть URL для Ajax-запросов, которые генерирует
jQuery-плагин AddressOK. В обработчике запросов к этому URL должен быть
подключен файл addressok.py.

Этот обработчик должен получать POST-запрос, передавать его в функцию
addressok.getData() (расположенную в подключенном файле addressok.py) в виде
Python-словаря и возвращать результат работы этой функции в виде JSON.

Пример обработчика (на примере микрофреймворка Flask):

.. code-block:: python
    
    @app.route('/addr_ajax', methods=['POST'])
    def addr_ajax():
        import json
        import addressok
        # Передаём POST-запрос, содержащийся в request.form, в функцию addressok.getData()
        addr_resp = addressok.getData(request.form)
        # Возвращаем результат в виде JSON
        return json.dumps(addr_resp)


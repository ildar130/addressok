Краткий пример подключения сервиса
===============================================================================

HTML-страница с формой ввода адреса
-------------------------------------------------------------------------------

.. code-blocK:: html

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
            <div>
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
-------------------------------------------------------------------------------

.. code-block:: php

    <?php

    require_once('addressok.php');

    if ($_SERVER['REQUEST_METHOD'] == 'POST') {
        // Отдаём в ответ на POST-запрос адресные данные
        echo AddressOK_GetData($_POST);
    }

    ?>

Серверная часть сайта на Python (back end) на примере Flask
-------------------------------------------------------------------------------

.. code-block:: python

    @app.route('/addr_ajax', methods=['POST'])
    def addr_ajax():
        import json
        import addressok
        # Передаём POST-запрос, содержащийся в request.form,
        # в функцию addressok.getData()
        addr_resp = addressok.getData(request.form)
        # Возвращаем результат в виде JSON
        return json.dumps(addr_resp)

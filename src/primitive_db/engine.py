# src/primitive_db/engine.py
import shlex

import prompt

from primitive_db import core, utils

DB_META_FILE = 'db_meta.json'

def print_help():
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> info <имя_таблицы> - вывести информацию о таблице")

    print("\n***Операции с данными***")
    print("Функции:")
    print(
        '<command> insert into <имя_таблицы> values '
        '(<значение1>, ...) - создать запись.'
    )
    print(
        '<command> select from <имя_таблицы> where <столбец> = '
        '<значение> - прочитать записи.'
    )
    print('<command> select from <имя_таблицы> - прочитать все записи.')
    print(
        '<command> update <имя_таблицы> set <столбец1> = <значение1> '
        'where <столбец_условия> = <значение_условия>'
    )
    print(
        '<command> delete from <имя_таблицы> where <столбец> = '
        '<значение> - удалить запись.'
    )

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")

def parse_condition(tokens):
    """Парсит токены вида ['age', '=', '28'] в {'age': '28'}."""
    if len(tokens) != 3 or tokens[1] != '=':
        return None
    return {tokens[0]: tokens[2]}

def parse_set_clause(tokens):
    """Парсит токены вида ['age', '=', '29'] в {'age': '29'}."""
    # Пример: ['age', '=', '29', 'name', '=', 'Bob'] -> {'age': '29', 'name': 'Bob'}
    if len(tokens) % 3 != 0:
        return None
    result = {}
    for i in range(0, len(tokens), 3):
        if tokens[i+1] != '=':
            return None
        result[tokens[i]] = tokens[i+2]
    return result

def parse_values(values_str):
    """Парсит строку значений в скобках: ('Sergei', 28, true) -> list."""
    values_str = values_str.strip()
    if not (values_str.startswith('(') and values_str.endswith(')')):
        return None
    inner = values_str[1:-1]
    
    # shlex с настройкой на запятую как разделитель пробелов
    lexer = shlex.shlex(inner, posix=True)
    lexer.whitespace += ','
    lexer.whitespace_split = True
    lexer.quotes = '"\''
    
    try:
        return list(lexer)
    except ValueError:
        return None

def run():
    print("\n***База данных***")
    print_help()

    while True:
        user_input = prompt.string('>>>Введите команду: ')
        if not user_input:
            continue

        try:
            args = shlex.split(user_input)
        except ValueError:
            print("Некорректный формат команды. Попробуйте снова.")
            continue

        if not args:
            continue

        command = args[0]
        rest = args[1:]

        metadata = utils.load_metadata(DB_META_FILE)

        # ---------- Команды ----------
        if command == 'exit':
            print("Выход из программы.")
            break

        elif command == 'help':
            print_help()

        elif command == 'list_tables':
            core.list_tables(metadata)

        elif command == 'create_table':
            if len(rest) < 2:
                print("Некорректное значение: недостаточно аргументов.")
                continue
            table_name, columns = rest[0], rest[1:]
            new_meta = core.create_table(metadata, table_name, columns)
            if new_meta is not None:
                utils.save_metadata(DB_META_FILE, new_meta)

        elif command == 'drop_table':
            if len(rest) != 1:
                print("Некорректное значение: неверное количество аргументов.")
                continue
            table_name = rest[0]
            new_meta = core.drop_table(metadata, table_name)
            if new_meta is not None:          # ← было: is not metadata
                utils.save_metadata(DB_META_FILE, new_meta)

        elif command == 'info':
            if len(rest) != 1:
                print("Некорректное значение: неверное количество аргументов.")
                continue
            table_name = rest[0]
            if table_name not in metadata:
                print(f'Ошибка: Таблица "{table_name}" не существует.')
                continue
            core.info(metadata, table_name)
            data = utils.load_table_data(table_name)
            print(f'Количество записей: {len(data)}')

        elif command == 'insert':
            if len(rest) < 4 or rest[0] != 'into' or rest[2] != 'values':
                print("Некорректное значение." \
                " Ожидается: insert into <table> values (...)")
                continue
            table_name = rest[1]
            values_str = ' '.join(rest[3:])
            values = parse_values(values_str)
            if values is None:
                print("Некорректное значение: не удалось разобрать values.")
                continue
            record = core.insert(metadata, table_name, values)
            if record is not None:
                data = utils.load_table_data(table_name)
                new_id = 1 if not data else max(r['ID'] for r in data) + 1
                record['ID'] = new_id
                data.append(record)
                utils.save_table_data(table_name, data)
                print(f'Запись с ID={new_id} успешно добавлена'
                       f'в таблицу "{table_name}".')

        elif command == 'select':
            if len(rest) < 2 or rest[0] != 'from':
                print(
                    "Некорректное значение. "
                    "Ожидается: select from <table> [where ...]"
                )
                continue
            table_name = rest[1]
            if table_name not in metadata:
                print(f'Ошибка: Таблица "{table_name}" не существует.')
                continue
            schema = metadata[table_name]
            data = utils.load_table_data(table_name)
            where_clause = None
            if len(rest) > 2:
                if rest[2] != 'where':
                    print(
                    "Некорректное значение. "
                    "Ожидается: select from <table> [where ...]"
                )
                    continue
                where_clause = parse_condition(rest[3:])
                if where_clause is None:
                    print("Некорректное значение: не удалось разобрать условие where.")
                    continue
            result = core.select(data, where_clause)
            core.print_table(table_name, schema, result)

        elif command == 'update':
            if len(rest) < 4:
                print(
                    "Некорректное значение. "
                    "Ожидается: update <table> set ... where ..."
                )
                continue
            table_name = rest[0]
            if table_name not in metadata:
                print(f'Ошибка: Таблица "{table_name}" не существует.')
                continue
            try:
                set_idx = rest.index('set')
                where_idx = rest.index('where')
            except ValueError:
                print("Некорректное значение: пропущены set или where.")
                continue
            set_clause = parse_set_clause(rest[set_idx+1:where_idx])
            where_clause = parse_condition(rest[where_idx+1:])
            if not set_clause or not where_clause:
                print("Некорректное значение в set или where.")
                continue
            data = utils.load_table_data(table_name)
            data, count, ids = core.update(data, set_clause, where_clause)
            if count:
                utils.save_table_data(table_name, data)
                ids_str = ', '.join(str(i) for i in ids)
                print(
                    f'Запись(и) с ID={ids_str} в таблице '
                    f'"{table_name}" успешно обновлена.'
                )
            else:
                print("Записей, удовлетворяющих условию, не найдено.")

        elif command == 'delete':
            if len(rest) < 4 or rest[0] != 'from':
                print("Некорректное значение. Ожидается: delete from <table> where ...")
                continue
            table_name = rest[1]
            if table_name not in metadata:
                print(f'Ошибка: Таблица "{table_name}" не существует.')
                continue
            if rest[2] != 'where':
                print("Некорректное значение: ожидается where.")
                continue
            where_clause = parse_condition(rest[3:])
            if not where_clause:
                print("Некорректное значение в where.")
                continue
            data = utils.load_table_data(table_name)
            data, count = core.delete(data, where_clause)
            if count:
                utils.save_table_data(table_name, data)
                print(f'Запись(и) удалены из таблицы "{table_name}".')
            else:
                print("Записей, удовлетворяющих условию, не найдено.")

        else:
            print(f'Функции "{command}" нет. Попробуйте снова.')
# src/primitive_db/engine.py
import shlex

import prompt

from primitive_db import core, utils

DB_META_FILE = 'db_meta.json'

def print_help():
    """Печатает справку для текущего режима."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")

def run():
    """Основной цикл программы."""
    print("\n***База данных***")
    print_help()

    while True:
        user_input = prompt.string('>>>Введите команду: ')
        
        try:
            args = shlex.split(user_input)
        except ValueError:
            print("Некорректный формат команды. Попробуйте снова.")
            continue

        if not args:
            continue

        command = args[0]
        command_args = args[1:]

        # Загружаем актуальные метаданные перед каждой командой
        metadata = utils.load_metadata(DB_META_FILE)

        if command == 'exit':
            print("Выход из программы.")
            break

        elif command == 'help':
            print_help()

        elif command == 'list_tables':
            core.list_tables(metadata)

        elif command == 'create_table':
            if len(command_args) < 2:
                print(
                    "Некорректное значение: "
                    "недостаточно аргументов. Попробуйте снова."
                )
                continue
            table_name = command_args[0]
            columns = command_args[1:]
            
            # Сохраняем результат и сохраняем метаданные в файл
            new_metadata = core.create_table(metadata, table_name, columns)
            if new_metadata is not metadata:  # Проверка, что таблица была создана
                 utils.save_metadata(DB_META_FILE, new_metadata)

        elif command == 'drop_table':
            if len(command_args) != 1:
                print(
                    "Некорректное значение: "
                    "неверное количество аргументов. Попробуйте снова."
                )
                continue
            table_name = command_args[0]
            
            new_metadata = core.drop_table(metadata, table_name)
            if new_metadata is not metadata:
                 utils.save_metadata(DB_META_FILE, new_metadata)

        else:
            print(f'Функции {command} нет. Попробуйте снова.')
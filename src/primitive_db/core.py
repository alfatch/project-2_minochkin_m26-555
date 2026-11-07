# src/primitive_db/core.py
import prettytable

VALID_TYPES = {'int', 'str', 'bool'}

# Работа с таблицами

def create_table(metadata, table_name, columns):
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return None  # ← было return metadata

    parsed_columns = [{'name': 'ID', 'type': 'int'}]
    for col in columns:
        if ':' not in col:
            print(f'Некорректное значение: {col}. Попробуйте снова.')
            return None  # ← было return metadata
        name, col_type = col.split(':', 1)
        if col_type not in VALID_TYPES:
            print(f'Некорректное значение: {col}. Попробуйте снова.')
            return None  # ← было return metadata
        parsed_columns.append({'name': name, 'type': col_type})

    metadata[table_name] = parsed_columns
    cols_str = ', '.join(f"{c['name']}:{c['type']}" for c in parsed_columns)
    print(f'Таблица "{table_name}" успешно создана со столбцами: {cols_str}')
    return metadata  

def drop_table(metadata, table_name):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return None                      # ← было: return metadata
    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata

def list_tables(metadata):
    if not metadata:
        print('Список таблиц пуст.')
        return
    for table_name in metadata.keys():
        print(f'- {table_name}')

# CRUD

def _validate_value(value, col_type):
    try:
        if col_type == 'int':
            return int(value)
        elif col_type == 'str':
            return str(value)
        elif col_type == 'bool':
            if str(value).lower() in ('true', '1', 'yes'):
                return True
            if str(value).lower() in ('false', '0', 'no'):
                return False
            return None
    except (ValueError, TypeError):
        return None
    return None

def insert(metadata, table_name, values):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return None

    schema = metadata[table_name]
    expected = len(schema) - 1  # без ID
    if len(values) != expected:
         print(
            f'Ошибка: Неверное количество значений. '
            f'Ожидается {expected}, получено {len(values)}.'
        )
         return None

    record = {}
    for i, col in enumerate(schema[1:], start=0):
        val = _validate_value(values[i], col['type'])
        if val is None:
            print(f'Некорректное значение: {values[i]}. Попробуйте снова.')
            return None
        record[col['name']] = val

    return record

def select(table_data, where_clause=None):
    if not where_clause:
        return table_data
    result = []
    for row in table_data:
        match = True
        for key, val in where_clause.items():
            if key not in row or str(row[key]) != str(val):
                match = False
                break
        if match:
            result.append(row)
    return result

def update(table_data, set_clause, where_clause):
    updated_count = 0
    updated_ids = []
    for row in table_data:
        match = True
        for key, val in where_clause.items():
            if key not in row or str(row[key]) != str(val):
                match = False
                break
        if match:
            for key, val in set_clause.items():
                row[key] = val
            updated_count += 1
            updated_ids.append(row.get('ID'))
    return table_data, updated_count, updated_ids

def delete(table_data, where_clause):
    to_delete = []
    for row in table_data:
        match = True
        for key, val in where_clause.items():
            if key not in row or str(row[key]) != str(val):
                match = False
                break
        if match:
            to_delete.append(row)
    for row in to_delete:
        table_data.remove(row)
    return table_data, len(to_delete)

def info(metadata, table_name):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return
    schema = metadata[table_name]
    cols_str = ', '.join(f"{c['name']}:{c['type']}" for c in schema)
    print(f'Таблица: {table_name}')
    print(f'Столбцы: {cols_str}')
    # Количество записей выводится отдельно в engine.py, т.к. нужны данные

def print_table(table_name, schema, data):
    table = prettytable.PrettyTable()
    table.field_names = [c['name'] for c in schema]
    for row in data:
        table.add_row([row.get(c['name'], '') for c in schema])
    print(table)
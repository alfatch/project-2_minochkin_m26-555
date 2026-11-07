# src/primitive_db/core.py

VALID_TYPES = {'int', 'str', 'bool'}

def create_table(metadata, table_name, columns):
    """
    Создаёт таблицу. 
    columns — список строк вида 'имя:тип'.
    """
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

    parsed_columns = []
    
    # Автоматически добавляем ID:int в начало
    parsed_columns.append({'name': 'ID', 'type': 'int'})

    for col in columns:
        if ':' not in col:
            print(f'Некорректное значение: {col}. Попробуйте снова.')
            return metadata
        
        name, col_type = col.split(':', 1)
        
        if col_type not in VALID_TYPES:
            print(f'Некорректное значение: {col}. Попробуйте снова.')
            return metadata
            
        parsed_columns.append({'name': name, 'type': col_type})

    metadata[table_name] = parsed_columns
    
    # Формируем красивый вывод (как в примере)
    cols_str = ', '.join(f"{c['name']}:{c['type']}" for c in parsed_columns)
    print(f'Таблица "{table_name}" успешно создана со столбцами: {cols_str}')
    
    return metadata


def drop_table(metadata, table_name):
    """Удаляет таблицу из метаданных."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


def list_tables(metadata):
    """Показывает список всех таблиц."""
    if not metadata:
        print('Список таблиц пуст.')
        return

    for table_name in metadata.keys():
        print(f'- {table_name}')
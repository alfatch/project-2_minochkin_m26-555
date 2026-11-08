# primitive_db

Простая CLI-база данных.

## Управление таблицами

Доступные команды:
- `create_table <имя_таблицы> <столбец1:тип> ...` — создать таблицу.
- `list_tables` — показать список всех таблиц.
- `drop_table <имя_таблицы>` — удалить таблицу.
- `help` — показать справку.
- `exit` — выйти из программы.

**Поддерживаемые типы данных:** `int`, `str`, `bool`.

### Пример использования

```bash
>>>Введите команду: create_table users name:str age:int is_active:bool
Таблица "users" успешно создана со столбцами: ID:int, name:str, age:int, is_active:bool

>>>Введите команду: list_tables
- users

>>>Введите команду: drop_table users
Таблица "users" успешно удалена.
## CRUD-операции

- `insert into <table> values (<v1>, <v2>, ...)` — создать запись.
- `select from <table> [where <col> = <val>]` — прочитать записи.
- `update <table> set <col> = <val> where <cond>` — обновить запись.
- `delete from <table> where <cond>` — удалить запись.
- `info <table>` — информация о таблице.
## Демонстрация работы

[![asciicast](https://asciinema.org/a/23xnqUdR3LxBnswI.svg)](https://asciinema.org/a/23xnqUdR3LxBnswI)

**Пример:**
```bash
>>> insert into users values ("Sergei", 28, true)
Запись с ID=1 успешно добавлена в таблицу "users".

>>> select from users
+----+--------+-----+-----------+
| ID |  name  | age | is_active |
+----+--------+-----+-----------+
| 1  | Sergei | 28  |    True   |
+----+--------+-----+-----------+
## Обработка ошибок и подтверждение действий

- Все операции с БД обёрнуты в декоратор `handle_db_errors`, который перехватывает ошибки и выводит понятные сообщения.
- Опасные операции (`drop_table`, `delete`) запрашивают подтверждение: `Вы уверены, что хотите выполнить "удаление таблицы"? [y/n]:`
- Время выполнения `insert` и `select` логируется.

## Демонстрация работы декораторов

https://asciinema.org/a/Tl7WsLMM1bvtFRPw
На записи показано:
- Запрос подтверждения при удалении записи (`delete`) и таблицы (`drop_table`).
- Логирование времени выполнения для `insert` и `select`.
- Отмена операции при ответе `n`.
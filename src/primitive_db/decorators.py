# src/primitive_db/decorators.py
import functools
import time

import prompt


def handle_db_errors(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(
                "Ошибка: Файл данных не найден. "
                "Возможно, база данных не инициализирована."
            )
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец {e} не найден.")
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")
    return wrapper


def confirm_action(action_name):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            answer = prompt.string(
                f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            )
            if answer.lower() != 'y':
                print("Операция отменена.")
                return None
            return func(*args, **kwargs)
        return wrapper
    return decorator


def log_time(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = func(*args, **kwargs)
        elapsed = time.monotonic() - start
        print(f"Функция {func.__name__} выполнилась за {elapsed:.3f} секунд.")
        return result
    return wrapper


def create_cacher():
    """Возвращает функцию-кэшер с замыканием."""
    cache = {}

    def cache_result(key, value_func):
        if key not in cache:
            cache[key] = value_func()
        return cache[key]

    def clear_cache():
        cache.clear()

    cache_result.clear = clear_cache
    return cache_result
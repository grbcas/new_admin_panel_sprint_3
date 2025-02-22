from time import sleep
from functools import wraps
from django.db.utils import OperationalError
from elastic_transport import ConnectionError
from settings import logger


def backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10):
    """
    Функция для повторного выполнения функции через некоторое время, если возникла ошибка.
    Использует наивный экспоненциальный рост времени повтора (factor) до граничного времени ожидания (border_sleep_time)

    Формула:
        t = start_sleep_time * (factor ^ n), если t < border_sleep_time
        t = border_sleep_time, иначе
    :param start_sleep_time: начальное время ожидания
    :param factor: во сколько раз нужно увеличивать время ожидания на каждой итерации
    :param border_sleep_time: максимальное время ожидания
    :return: результат выполнения функции
    """

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            t_sleep = start_sleep_time
            n = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except (
                        OperationalError,
                        ConnectionError,
                        TimeoutError
                ) as e:
                    logger.warning(f"Exception occurred: {e}. Retrying in {t_sleep} seconds...")
                    sleep(t_sleep)
                    n += 1
                    t_sleep = min(start_sleep_time * (factor ** n), border_sleep_time)
        return inner

    return func_wrapper

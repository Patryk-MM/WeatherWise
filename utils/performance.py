import time
import functools
import psutil
import os

def measure_time(func):
    """Dekorator mierzący czas wykonania funkcji"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.3f}s")
        return result
    return wrapper

def profile_function(func):
    """Dekorator mierzący zużycie CPU i pamięci"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        process = psutil.Process(os.getpid())
        before_mem = process.memory_info().rss / (1024 * 1024)
        before_cpu = psutil.cpu_percent(interval=None)

        result = func(*args, **kwargs)

        after_mem = process.memory_info().rss / (1024 * 1024)
        after_cpu = psutil.cpu_percent(interval=None)
        print(f"{func.__name__} – RAM: {after_mem - before_mem:.2f} MB | CPU: {after_cpu:.2f}%")
        return result
    return wrapper

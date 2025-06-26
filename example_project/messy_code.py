#!/usr/bin/env python3
"""
Пример грязного Python кода для демонстрации CleanCodeZap.
Этот файл содержит различные проблемы, которые должен исправить инструмент.
"""

# Неиспользуемые импорты
import requests
from datetime import datetime

# Неиспользуемые переменные
unused_variable = "Это неиспользуемая переменная"
another_unused = 42
UNUSED_CONSTANT = "КОНСТАНТА"

# Закомментированный код (должен быть удален)
# def old_function():
#     return "старый код"
#
# class OldClass:
#     def __init__(self):
#         self.value = 10
#
# # Еще комментарии с кодом
# if True:
#     print("закомментированный код")
#     for i in range(10):
#         result = i * 2


def badly_formatted_function(x, y, z):
    """Плохо отформатированная функция."""
    # Плохое форматирование
    if x > 0 and y < 10:
        result = x + y * z
        return result
    else:
        return None


class BadlyFormattedClass:
    """Класс с плохим форматированием."""

    def __init__(self, name, age):
        self.name = name
        self.age = age

    def get_info(self):
        return f"{self.name} is {self.age} years old"


def function_with_used_imports():
    """Функция, которая использует некоторые импорты."""
    current_time = datetime.now()
    print(f"Текущее время: {current_time}")

    # Используем requests
    try:
        response = requests.get("https://httpbin.org/json")
        data = response.json()
        return data
    except:
        return {}


# Неиспользуемые переменные в функции
def function_with_unused_vars():
    """Функция с неиспользуемыми переменными."""
    used_var = "используется"

    print(f"Значение: {used_var}")


# Дублированные ключи в словаре (для aggressive режима)
config = {
    "debug": True,
    "port": 8080,
    "debug": False,  # Дублированный ключ
    "host": "localhost",
}


# # Много закомментированного кода
# def commented_function():
#     """Закомментированная функция."""
#     x = 10
#     y = 20
#     return x + y
#
# # Закомментированный цикл
# for item in range(100):
#     print(f"Item: {item}")
#     if item % 10 == 0:
#         print("Divisible by 10")
#
# # Закомментированное условие
# if config.get('debug'):
#     print("Debug mode enabled")
#     logging.level = DEBUG


def main():
    """Главная функция."""
    print("Демонстрация CleanCodeZap")

    # Создаем экземпляр класса
    obj = BadlyFormattedClass("Иван", 25)
    print(obj.get_info())

    # Вызываем функцию
    result = badly_formatted_function(1, 2, 3)
    print(f"Результат: {result}")

    # Вызываем функцию с импортами
    data = function_with_used_imports()
    print(f"Получены данные: {data}")

    # Вызываем функцию с неиспользуемыми переменными
    function_with_unused_vars()


if __name__ == "__main__":
    main()

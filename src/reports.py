import functools
from datetime import datetime, timedelta

import pandas as pd


def report_decorator(file_name=None):
    """Декоратор для записи результата функции"""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if file_name:
                output_file = file_name
            else:
                output_file = f'report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'

            # Преобразование DataFrame в строку
            result_str = result.to_string(index=False)

            with open(output_file, "w", encoding="utf-8") as file:
                file.write(result_str)
            return result

        return wrapper

    return decorator


@report_decorator()
def spending_by_category(transactions, category, date):
    """Возвращает траты по категории за последние три месяца от заданной даты"""

    # Преобразование строки даты в объект datetime
    if date is not None:
        if isinstance(date, str):
            try:
                date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    date = datetime.strptime(date, "%Y-%m-%d")
                except ValueError:
                    raise ValueError("date должен быть в формате 'YYYY-MM-DD' или 'YYYY-MM-DD HH:MM:SS'")
        elif not isinstance(date, datetime):
            raise ValueError("date должен быть объектом datetime")
    else:
        date = datetime.today()

    # Приведение "Дата операции" к datetime
    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], format="mixed", dayfirst=True)

    # Фильтрация транзакций по категории
    filtered_by_category = transactions[transactions["Категория"] == category]

    # Фильтрация транзакций по дате
    start_date = date - timedelta(days=90)
    filtered_by_date = filtered_by_category[
        (filtered_by_category["Дата операции"] >= start_date) & (filtered_by_category["Дата операции"] <= date)
    ]

    # Возвращение DataFrame с транзакциями по категории за последние три месяца
    return filtered_by_date

from src.reports import spending_by_category
from src.services import dataframe_to_dict_with_str, search_transactions
from src.utils import (API_KEY_CURRENCY, API_KEY_STOCK, data_from_excel, filter_transactions_by_date, data_from_user_settings, text_of_the_greeting, calculate_card_info, top_transactions, info_currency_rates, info_stock_prices)
from src.views import form_json_response


if API_KEY_CURRENCY is None:
    raise ValueError("API_KEY_CURRENCY не найден в окружении")
if API_KEY_STOCK is None:
    raise ValueError("API_KEY_STOCK не найден в окружении")

if __name__ == "__main__":
    # ========================= Веб страницы: «Главная» =========================
    print("===== Веб страницы: «Главная» =====", "\n")
    # Заданные значения для выполнения функций
    date_time_str = "2020-04-27 19:30:30"
    file_path_transactions = "data/operations.xlsx"
    file_path_user_settings = "data/user_settings.json"
    base_currency = "RUB"

    # Загрузка данных транзакций
    all_transactions = data_from_excel(file_path_transactions)

    # Фильтрация транзакций по дате
    transactions = filter_transactions_by_date(all_transactions, date_time_str)

    # Загрузка пользовательских настроек
    user_currencies, user_stocks = data_from_user_settings(file_path_user_settings)

    # Генерация приветствия
    greeting = text_of_the_greeting(date_time_str)

    # Вычисление информации по картам
    card_info = calculate_card_info(transactions)

    # Получение топ-5 транзакций
    top_transactions = top_transactions(transactions)

    # Получение курсов валют
    currency_rates = info_currency_rates(API_KEY_CURRENCY, base_currency, user_currencies)

    # Получение цен на акции
    stock_prices = info_stock_prices(API_KEY_STOCK, user_stocks)

    # Формирование JSON-ответа
    json_response = form_json_response(greeting, card_info, top_transactions, currency_rates, stock_prices)

    # Печать JSON-ответа
    print(json_response)

    # ========================= Сервисы: «Простой поиск» =========================
    print("\n\n", "===== Сервисы: «Простой поиск» =====", "\n")
    # Получение транзакций в виде словаря
    transactions_dict = dataframe_to_dict_with_str(all_transactions)

    # Запуск простого поиска и печать JSON-ответа
    print(search_transactions(transactions_dict, "Ozon.ru"))

    # ========================= Отчеты: «Траты по категории» =========================
    print("\n\n", "===== Отчеты: «Траты по категории» =====", "\n")
    # Выводим траты по заданной категории за последние три месяца (от переданной даты)
    print(spending_by_category(all_transactions, "Супермаркеты", date_time_str))
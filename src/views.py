import json

from src.utils import (API_KEY_CURRENCY, API_KEY_STOCK, calculate_card_info, data_from_user_settings,
                       filter_transactions_by_date, info_currency_rates, info_stock_prices, text_of_the_greeting,
                       top_transactions)


def get_main_page(date_time_str, all_transactions, file_path_user_settings, base_currency):
    # Фильтрация транзакций по дате
    transactions = filter_transactions_by_date(all_transactions, date_time_str)

    # Загрузка пользовательских настроек
    user_currencies, user_stocks = data_from_user_settings(file_path_user_settings)

    # Генерация приветствия
    greeting = text_of_the_greeting()

    # Вычисление информации по картам
    card_info = calculate_card_info(transactions)

    # Получение топ-5 транзакций
    top_5_transactions = top_transactions(transactions)

    # Получение курсов валют
    currency_rates = info_currency_rates(API_KEY_CURRENCY, base_currency, user_currencies)

    # Получение цен на акции
    stock_prices = info_stock_prices(API_KEY_STOCK, user_stocks)

    # Формирование JSON-ответа
    response = {
        "greeting": greeting,
        "cards": card_info,
        "top_transactions": top_5_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }
    json_response = json.dumps(response, ensure_ascii=False, indent=4)
    return json_response

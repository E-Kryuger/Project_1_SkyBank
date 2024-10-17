from src.reports import spending_by_category
from src.services import dataframe_to_dict_with_str, search_transactions
from src.utils import API_KEY_CURRENCY, API_KEY_STOCK, data_from_excel
from src.views import get_main_page

if API_KEY_CURRENCY is None:
    raise ValueError("API_KEY_CURRENCY не найден в окружении")
if API_KEY_STOCK is None:
    raise ValueError("API_KEY_STOCK не найден в окружении")

if __name__ == "__main__":
    # Заданные значения для выполнения функций
    date_time_str = "2020-04-27 19:30:30"
    file_path_user_settings = "../data/user_settings.json"
    base_currency = "RUB"
    all_transactions = data_from_excel("../data/operations.xlsx")

    # ========================= Веб страницы: «Главная» =========================
    print("===== Веб страницы: «Главная» =====", "\n")

    # Печать JSON-ответа
    print(get_main_page(date_time_str, all_transactions, file_path_user_settings, base_currency))

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

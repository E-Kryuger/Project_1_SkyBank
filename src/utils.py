import json
import logging
import os
from datetime import datetime

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY_CURRENCY = os.getenv("API_KEY_CURRENCY")
API_KEY_STOCK = os.getenv("API_KEY_STOCK")

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def text_of_the_greeting(current_time=datetime.now()):
    """Функция, которая смотрит на текущее время и возвращает приветствие"""

    logging.info(f"Определение времени суток для времени {current_time}")

    if 5 <= current_time.hour < 11:
        greeting = "Доброе утро"
    elif 11 <= current_time.hour < 17:
        greeting = "Добрый день"
    elif 17 <= current_time.hour < 23:
        greeting = "Добрый вечер"
    else:
        greeting = "Доброй ночи"
    return greeting


def data_from_excel(file_path):
    """Читает Excel-файл и возвращает список словарей с данными о финансовых транзакциях"""
    logging.info(f"Загрузка транзакций из файла: {file_path}")
    try:
        transactions = pd.read_excel(file_path)
    except FileNotFoundError:
        logging.error(f"Файл '{file_path}' не найден")
        raise ValueError(f"Файл '{file_path}' не найден")
    except ValueError:
        logging.error(f"Файл '{file_path}' не является допустимым Excel файлом")
        raise ValueError(f"Файл '{file_path}' не является допустимым Excel файлом")

    logging.info(f"Транзакции успешно загружены. Количество записей: {len(transactions)}")
    return transactions


def filter_transactions_by_date(transactions, date_time_str):
    """Фильтрует транзакции по заданной дате"""

    logging.info(f"Для фильтрации транзакций задана дата: {date_time_str}")

    try:
        end_date = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        logging.error(f"Некорректный формат даты и времени: {date_time_str}")
        raise ValueError("Некорректный формат даты и времени")
    start_date = pd.Timestamp(year=end_date.year, month=end_date.month, day=1, hour=0, minute=0, second=0)

    # Создание копии перед выполнением
    transactions_copy = transactions.copy()

    # Преобразование данных из 'Дата операции' в datetime
    transactions_copy.loc[:, "Дата операции"] = pd.to_datetime(
        transactions_copy["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce"
    )

    # Фильтрация транзакций по датам
    filtered_transactions = transactions_copy.loc[
        (transactions_copy["Дата операции"] >= start_date) & (transactions_copy["Дата операции"] <= end_date)
    ]

    start = start_date.strftime("%Y-%m-%d %H:%M:%S")
    logging.info(f"Найдено {len(filtered_transactions)} транзакций с {start} по {date_time_str}")

    return filtered_transactions


def calculate_card_info(transactions):
    """Вычисляет информацию по картам"""

    logging.info("Вычисление информации по картам")
    if "Номер карты" not in transactions.columns or "Сумма операции" not in transactions.columns:
        logging.error("Необходимые столбцы отсутствуют в данных транзакций")
        raise ValueError("Необходимые столбцы отсутствуют в данных транзакций")

    # Вычисление общей суммы расходов и кешбэка по картам
    card_info = (
        transactions.groupby("Номер карты")
        .agg(
            total_spent=pd.NamedAgg(column="Сумма операции", aggfunc="sum"),
            cashback=pd.NamedAgg(column="Сумма операции", aggfunc=lambda x: round(sum(x) * 0.01, 2)),
        )
        .reset_index()
    )

    # 4 цифры номера карты
    card_info["last_digits"] = card_info["Номер карты"].astype(str).str[-4:]

    # Формирование списка словарей для JSON
    cards_data = card_info.loc[:, ["last_digits", "total_spent", "cashback"]].to_dict("records")

    logging.info("Информация по картам успешно вычислена")

    return cards_data


def top_transactions(transactions):
    """Функция, которая ищет топ 5 транзакций и выводит данные по ним"""

    logging.info("Определение топ-5 транзакций по сумме платежа")
    if "Дата операции" not in transactions.columns or "Сумма платежа" not in transactions.columns:
        logging.error("В транзакциях DataFrame отсутствуют требуемые столбцы")
        raise ValueError("В транзакциях DataFrame отсутствуют требуемые столбцы")

    # Преобразование столбца даты в формат datetime
    transactions["Дата операции"] = pd.to_datetime(
        transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce"
    )

    # Сортировка по сумме платежа в порядке убывания и выбор топ-5 транзакций
    sorted_transactions = transactions.sort_values(by="Сумма платежа", ascending=False)
    top_5_transactions = sorted_transactions.head(5)

    # Формирование списка словарей
    top_transactions_data = top_5_transactions[["Дата операции", "Сумма платежа", "Категория", "Описание"]].copy()
    top_transactions_data["Дата операции"] = top_transactions_data["Дата операции"].dt.strftime("%d.%m.%Y")
    top_transactions_data = top_transactions_data.rename(
        columns={
            "Дата операции": "date",
            "Сумма платежа": "amount",
            "Категория": "category",
            "Описание": "description",
        }
    )

    logging.info("Топ-5 транзакций успешно определены")

    return top_transactions_data.to_dict(orient="records")


def data_from_user_settings(file_path_user_settings):
    """Экспорт данных из user_settings.json"""
    logging.info(f"Загрузка пользовательских настроек из файла: {file_path_user_settings}")
    try:
        with open(file_path_user_settings, "r", encoding="utf-8") as file:
            user_settings = json.load(file)
    except FileNotFoundError:
        logging.error(f"Файл '{file_path_user_settings}' не найден")
        raise ValueError(f"Файл '{file_path_user_settings}' не найден")

    user_currencies = user_settings["user_currencies"]
    user_stocks = user_settings["user_stocks"]

    logging.info(f"Успешно загружены пользовательские настройки: {user_currencies}, {user_stocks}")

    return user_currencies, user_stocks


def info_currency_rates(API_KEY_CURRENCY, base_currency, user_currencies):
    """Функция, которая собирает данные по валютам, исходя из пользовательских настроек"""
    logging.info(f"Запрос курсов валют для базовой валюты: {base_currency}")

    url = f"https://v6.exchangerate-api.com/v6/{API_KEY_CURRENCY}/latest/{base_currency}"
    response = requests.get(url)
    data = response.json()
    rates = data.get("conversion_rates", {})
    currency_rates = []

    for currency in user_currencies:
        if currency in rates:
            # Преобразование курса валюты к рублю
            rate_to_rub = round(1 / rates[currency], 2)
            currency_rates.append({"currency": currency, "rate": rate_to_rub})
            logging.info(f"Курс для {currency}: {rate_to_rub} RUB")
        else:
            logging.info(f"Курс для валюты {currency} не найден")
            print(f"Курс для валюты {currency} не найден")

    logging.info("Курсы валют успешно получены")
    return currency_rates


def info_stock_prices(API_KEY_STOCK, user_stocks):
    """Функция, которая собирает данные по акциям, исходя из пользовательских настроек"""
    logging.info(f"Запрос цен на акции: {', '.join(user_stocks)}")
    stock_prices = []

    for stock in user_stocks:
        url = "https://finnhub.io/api/v1/quote"
        params = {"symbol": stock, "token": API_KEY_STOCK}
        response = requests.get(url, params=params)
        data = response.json()

        if "c" in data:
            stock_prices.append({"stock": stock, "price": float(data["c"])})
            logging.info(f"Цена для {stock}: {data['c']} USD")
        else:
            logging.info(f"Ошибка получения данных для акции: {stock}")
            print(f"Ошибка получения данных для акции: {stock}")

    logging.info("Цены на акции успешно получены.")
    return stock_prices

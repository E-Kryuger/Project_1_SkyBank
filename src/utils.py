from datetime import datetime
import pandas as pd
import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY_CURRENCY = os.getenv("API_KEY_CURRENCY")
API_KEY_STOCK = os.getenv("API_KEY_STOCK")


def text_of_the_greeting(date_time_str):
    """Функция, которая смотрит на текущее время и возвращает приветствие"""

    current_time = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")

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
    transactions = pd.read_excel(file_path)
    return transactions


def filter_transactions_by_date(transactions, date_time_str):
    """Фильтрует транзакции по заданной дате"""
    end_date = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")
    start_date = end_date - pd.Timedelta(days=1)

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

    return filtered_transactions


def calculate_card_info(transactions):
    """Вычисляет информацию по картам"""

    # Вычисление общей суммы расходов и кешбэка по картам
    card_info = (
        transactions.groupby("Номер карты")
        .agg(
            total_spent=pd.NamedAgg(column="Сумма операции", aggfunc="sum"),
            cashback=pd.NamedAgg(column="Сумма операции", aggfunc=lambda x: sum(x) * 0.01),
        )
        .reset_index()
    )

    # 4 цифры номера карты
    card_info["last_digits"] = card_info["Номер карты"].astype(str).str[-4:]

    # Формирование списка словарей для JSON
    cards_data = []
    for _, row in card_info.iterrows():
        cards_data.append(
            {"last_digits": row["last_digits"], "total_spent": row["total_spent"], "cashback": row["cashback"]}
        )

    return cards_data


def top_transactions(transactions):
    """Функция, которая ищет топ 5 транзакций и выводит данные по ним"""
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

    return top_transactions_data.to_dict(orient="records")


def data_from_user_settings(file_path):
    """Экспорт данных из user_settings.json"""
    with open(file_path, "r", encoding="utf-8") as file:
        user_settings = json.load(file)

    user_currencies = user_settings["user_currencies"]
    user_stocks = user_settings["user_stocks"]

    return user_currencies, user_stocks


def info_currency_rates(api_key, base_currency, target_currencies):
    """Функция, которая собирает данные по валютам, исходя из пользовательских настроек"""
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{base_currency}"
    response = requests.get(url)
    data = response.json()
    rates = data.get("conversion_rates", {})
    currency_rates = []

    for currency in target_currencies:
        if currency in rates:
            # Преобразование курса валюты к рублю
            rate_to_rub = round(1 / rates[currency], 2)
            currency_rates.append({"currency": currency, "rate": rate_to_rub})

    return currency_rates


def info_stock_prices(api_key, stocks):
    """Функция, которая собирает данные по акциям, исходя из пользовательских настроек"""
    stock_prices = []

    for stock in stocks:
        url = "https://finnhub.io/api/v1/quote"
        params = {"symbol": stock, "token": api_key}
        response = requests.get(url, params=params)
        data = response.json()

        if "c" in data:
            stock_prices.append({"stock": stock, "price": float(data["c"])})

    return stock_prices

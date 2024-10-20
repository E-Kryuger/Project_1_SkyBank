import json
from datetime import datetime
from unittest.mock import mock_open, patch

import pandas as pd
import pytest

from src.utils import (calculate_card_info, data_from_excel, data_from_user_settings, filter_transactions_by_date,
                       text_of_the_greeting, top_transactions)


@pytest.mark.parametrize(
    "current_time, expected",
    [
        (datetime(2023, 7, 27, 9, 0, 0), "Доброе утро"),
        (datetime(2023, 7, 27, 13, 0, 0), "Добрый день"),
        (datetime(2023, 7, 27, 19, 0, 0), "Добрый вечер"),
        (datetime(2023, 7, 27, 23, 0, 0), "Доброй ночи"),
    ],
)
def test_text_of_the_greeting(current_time, expected):
    """Тестирует функцию text_of_the_greeting для разных времен суток"""
    assert text_of_the_greeting(current_time) == expected


def test_data_from_excel(data_transactions):
    """Тестирует корректную загрузку транзакций из валидного Excel файла"""
    df = pd.DataFrame(data_transactions)

    with patch("pandas.read_excel") as mock_read_excel:
        mock_read_excel.return_value = df
        result = data_from_excel("valid_file.xlsx")
        assert result.equals(df)


def test_data_from_excel_file_not_found():
    """Тестирует возникновение ошибки при отсутствии файла"""
    with patch("pandas.read_excel", side_effect=FileNotFoundError):
        with pytest.raises(ValueError, match="Файл 'missing_file.xlsx' не найден."):
            data_from_excel("missing_file.xlsx")


def test_data_from_excel_empty_file():
    """Тестирует корректную загрузку при пустом Excel файле"""
    empty_df = pd.DataFrame()

    with patch("pandas.read_excel") as mock_read_excel:
        mock_read_excel.return_value = empty_df
        result = data_from_excel("empty_file.xlsx")
        assert result.equals(empty_df)


def test_filter_transactions_by_date_no_transactions_in_date_range(data_transactions_date_time):
    """
    Тестирует фильтрацию транзакций, если в заданном диапазоне дат нет транзакций.
    """
    df = pd.DataFrame(data_transactions_date_time[0])
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")

    date_time_str = "2024-07-27 12:00:00"
    filtered_df = filter_transactions_by_date(df, date_time_str)

    assert filtered_df.empty


def test_filter_transactions_by_date_transactions_near_boundaries():
    """
    Тестирует фильтрацию транзакций на границах диапазона дат.
    """
    data = {
        "Дата операции": ["26.07.2023 12:00:00", "27.07.2023 12:00:00", "28.07.2023 12:00:00"],
        "Сумма операции": [100, 200, 300],
        "Категория": ["Продукты", "Развлечения", "Одежда"],
    }
    df = pd.DataFrame(data)
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")

    date_time_str = "2023-07-27 12:00:00"
    filtered_df = filter_transactions_by_date(df, date_time_str)

    expected_data = {
        "Дата операции": ["26.07.2023 12:00:00", "27.07.2023 12:00:00"],
        "Сумма операции": [100, 200],
        "Категория": ["Продукты", "Развлечения"],
    }
    expected_df = pd.DataFrame(expected_data)
    expected_df["Дата операции"] = pd.to_datetime(expected_df["Дата операции"], format="%d.%m.%Y %H:%M:%S")

    assert filtered_df.reset_index(drop=True).equals(expected_df.reset_index(drop=True))


def test_calculate_card_info_valid_data():
    """
    Тестирует корректную обработку валидных данных.
    """
    data = {
        "Номер карты": ["1234567812345678", "1234567812345678", "8765432187654321"],
        "Сумма операции": [100, 200, 300],
    }
    df = pd.DataFrame(data)

    result = calculate_card_info(df)

    expected_result = [
        {"last_digits": "5678", "total_spent": 300, "cashback": 3.0},
        {"last_digits": "4321", "total_spent": 300, "cashback": 3.0},
    ]

    assert result == expected_result


def test_calculate_card_info_empty_dataframe():
    """
    Тестирует обработку пустого DataFrame.
    """
    df = pd.DataFrame(columns=["Номер карты", "Сумма операции"])

    result = calculate_card_info(df)

    expected_result = []

    assert result == expected_result


def test_calculate_card_info_single_card_multiple_transactions():
    """
    Тестирует обработку данных для одной карты с несколькими транзакциями.
    """
    data = {
        "Номер карты": ["1234567812345678", "1234567812345678", "1234567812345678"],
        "Сумма операции": [50, 150, 200],
    }
    df = pd.DataFrame(data)

    result = calculate_card_info(df)

    expected_result = [{"last_digits": "5678", "total_spent": 400, "cashback": 4.0}]

    assert result == expected_result


def test_calculate_card_info_multiple_cards_single_transaction_each():
    """
    Тестирует обработку данных для нескольких карт с одной транзакцией для каждой.
    """
    data = {
        "Номер карты": ["1234567812345678", "8765432187654321", "1122334455667788"],
        "Сумма операции": [100, 200, 300],
    }
    df = pd.DataFrame(data)

    result = calculate_card_info(df)

    expected_result = [
        {"last_digits": "5678", "total_spent": 100, "cashback": 1.0},
        {"last_digits": "4321", "total_spent": 200, "cashback": 2.0},
        {"last_digits": "7788", "total_spent": 300, "cashback": 3.0},
    ]

    # Сортировка результатов для корректного сравнения
    result = sorted(result, key=lambda x: x["last_digits"])
    expected_result = sorted(expected_result, key=lambda x: x["last_digits"])

    assert result == expected_result


def test_top_transactions_valid_data():
    """
    Тестирует определение топ-5 транзакций с корректными данными.
    """
    data = {
        "Дата операции": [
            "26.07.2023 12:00:00",
            "27.07.2023 12:00:00",
            "28.07.2023 12:00:00",
            "29.07.2023 12:00:00",
            "30.07.2023 12:00:00",
            "31.07.2023 12:00:00",
        ],
        "Сумма платежа": [100, 200, 300, 400, 500, 600],
        "Категория": ["Продукты", "Развлечения", "Одежда", "Техника", "Транспорт", "Рестораны"],
        "Описание": [
            "Покупка в супермаркете",
            "Билеты в кино",
            "Покупка одежды",
            "Покупка техники",
            "Такси",
            "Ужин в ресторане",
        ],
    }
    df = pd.DataFrame(data)

    expected_data = [
        {"date": "31.07.2023", "amount": 600, "category": "Рестораны", "description": "Ужин в ресторане"},
        {"date": "30.07.2023", "amount": 500, "category": "Транспорт", "description": "Такси"},
        {"date": "29.07.2023", "amount": 400, "category": "Техника", "description": "Покупка техники"},
        {"date": "28.07.2023", "amount": 300, "category": "Одежда", "description": "Покупка одежды"},
        {"date": "27.07.2023", "amount": 200, "category": "Развлечения", "description": "Билеты в кино"},
    ]

    result = top_transactions(df)
    assert result == expected_data


def test_top_transactions_insufficient_data():
    """
    Тестирует определение топ-5 транзакций, если данных меньше пяти.
    """
    data = {
        "Дата операции": ["26.07.2023 12:00:00", "27.07.2023 12:00:00"],
        "Сумма платежа": [100, 200],
        "Категория": ["Продукты", "Развлечения"],
        "Описание": ["Покупка в супермаркете", "Билеты в кино"],
    }
    df = pd.DataFrame(data)

    expected_data = [
        {"date": "27.07.2023", "amount": 200, "category": "Развлечения", "description": "Билеты в кино"},
        {"date": "26.07.2023", "amount": 100, "category": "Продукты", "description": "Покупка в супермаркете"},
    ]

    result = top_transactions(df)
    assert result == expected_data


def test_data_from_user_settings():
    """
    Тестирует успешную загрузку и извлечение настроек пользователя.
    """
    mock_file_data = json.dumps({"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "GOOGL"]})

    with patch("builtins.open", mock_open(read_data=mock_file_data)):
        user_currencies, user_stocks = data_from_user_settings("dummy_path")

    assert user_currencies == ["USD", "EUR"]
    assert user_stocks == ["AAPL", "GOOGL"]

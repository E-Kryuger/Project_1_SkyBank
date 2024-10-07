import json



def dataframe_to_dict_with_str(df):
    """Преобразует DataFrame в список словарей"""
    result = []
    for a, row in df.iterrows():
        transaction = row.to_dict()
        if "Категория" in transaction:
            transaction["Категория"] = str(transaction["Категория"])
        if "Описание" in transaction:
            transaction["Описание"] = str(transaction["Описание"])
        result.append(transaction)
    return result


def search_transactions(transactions, query):
    """Ищет транзакции по поисковому запросу"""

    matching_transactions = [
        transaction
        for transaction in transactions
        if isinstance(transaction, dict)
        and (
            query.lower() in transaction.get("Описание", "").lower()
            or query.lower() in transaction.get("Категория", "").lower()
        )
    ]

    json_response = json.dumps(matching_transactions, ensure_ascii=False)
    return json_response

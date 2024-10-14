import json


def form_json_response(greeting, card_info, top_transactions, currency_rates, stock_prices):
    """Формирует JSON-ответ"""
    response = {
        "greeting": greeting,
        "cards": card_info,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }
    return json.dumps(response, ensure_ascii=False, indent=4)

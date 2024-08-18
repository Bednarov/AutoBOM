import urllib.request
import urllib.error
import json
from time import sleep

from api import Client


class API:
    @staticmethod
    def search_page(product_name: str, auth: list, category: str = None, page: int = None) -> dict:
        sleep(0.1)
        token = auth[0]
        secret = auth[1]

        client = Client(token, secret)

        if len(product_name) > 40:
            product_name = product_name[:40]

        parameters = {
            'SearchPlain': product_name,
            'Country': 'PL',
            'Language': 'en',
            'SearchWithStock': 'true',
            'SearchOrder': 'PRICE_FIRST_QUANTITY',
            'SearchOrderType': 'ASC'
        }
        if category:
            parameters.update({'SearchCategory': category})
        if page:
            parameters.update({'SearchPage': str(page)})

        try:
            response = urllib.request.urlopen(client.request('/Products/Search', parameters))
            response_str = response.read().decode('utf-8')
            response_json = json.loads(response_str)
            products_list = response_json["Data"]["ProductList"]
            products_found = int(response_json["Data"]["Amount"])
            return {
                "HowManyFound": products_found,
                "ProductList": products_list,
                "APIError": None
            }

        except urllib.error.URLError as e:
            print(f"API error!: '{e.reason}'")
            return {
                "HowManyFound": -1,
                "ProductList": [],
                "APIError": e.reason
            }

    @staticmethod
    def get_product_price_and_stock_multiple(symbol_list: list, auth: list) -> list:
        sleep(0.5)
        print(f"Getting prices and stocks...")
        token = auth[0]
        secret = auth[1]

        client = Client(token, secret)
        symbol_stock_price_list = []
        while symbol_list:
            parameters = {
                'Country': 'PL',
                'Language': 'en',
                'Currency': 'PLN',
            }
            for index, symbol in enumerate(symbol_list):
                if index > 9:
                    break
                parameters.update({f"SymbolList[{index}]": f"{symbol}"})
                symbol_list.remove(symbol)

            try:
                response = urllib.request.urlopen(client.request('/Products/GetPricesAndStocks', parameters))
                response_str = response.read().decode('utf-8')
                response_json = json.loads(response_str)

                product_list = response_json["Data"]["ProductList"]
                for product in product_list:
                    symbol_stock_price_list.append({
                        "Symbol": product["Symbol"],
                        "Stock": int(product["Amount"]),
                        "PriceList": product["PriceList"]
                    })
            except urllib.error.URLError as e:
                print(f"API error!: '{e.reason}'")
                return []
        return symbol_stock_price_list

    @staticmethod
    def get_all_symbols(auth: list) -> list:
        print(f"> Getting all symbols...")
        token = auth[0]
        secret = auth[1]

        client = Client(token, secret)
        parameters = {
            'Country': 'PL',
            'Language': 'en',
        }

        try:
            response = urllib.request.urlopen(client.request('/Products/GetSymbols', parameters))
            response_str = response.read().decode('utf-8')
            response_json = json.loads(response_str)

            found_symbols_list = response_json["Data"]["SymbolList"]
            print(f"Got {len(found_symbols_list)} symbols from TME.")
            sleep(1)
            return found_symbols_list

        except urllib.error.URLError as e:
            print(f"API error!: '{e.reason}'")
            return []

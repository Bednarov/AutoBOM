import urllib.request
import urllib.error
import json
from time import sleep

from api import Client


Categories = {
    "R": "Resistors",
    "L": "Inductors",
    "C": "Capacitors",
    "Q": "Transistors",
    "D": "Diodes",
}


class API:
    @staticmethod
    def search_page(product_name: str, auth: list, category: str = None, page: int = None) -> dict:
        sleep(0.1)
        token = auth[0]
        secret = auth[1]

        client = Client(token, secret)

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
    def get_product_price_and_stock_multiple(symbol_list: list, auth: list) -> list:  # TODO: Handle not being able to request for more than 10 at a time
        sleep(0.5)
        print(f"Getting prices and stocks...")
        token = auth[0]
        secret = auth[1]

        client = Client(token, secret)
        parameters = {
            'Country': 'PL',
            'Language': 'en',
            'Currency': 'PLN',
        }
        for index, symbol in enumerate(symbol_list):
            if index > 9:
                break
            parameters.update({f"SymbolList[{index}]": f"{symbol}"})

        try:
            response = urllib.request.urlopen(client.request('/Products/GetPricesAndStocks', parameters))
            response_str = response.read().decode('utf-8')
            response_json = json.loads(response_str)

            product_list = response_json["Data"]["ProductList"]
            symbol_stock_price_list = []
            for product in product_list:
                symbol_stock_price_list.append({
                    "Symbol": product["Symbol"],
                    "Stock": int(product["Amount"]),
                    "PriceList": product["PriceList"]
                })
            return symbol_stock_price_list

        except urllib.error.URLError as e:
            print(f"API error!: '{e.reason}'")
            return []

    @staticmethod
    def get_specific_product_info(product_name: str, auth: list, dont_print: bool = True) -> dict:
        if not dont_print:
            print(f"Getting information about '{product_name}'...")
        sleep(0.1)
        token = auth[0]
        secret = auth[1]

        client = Client(token, secret)
        parameters = {
            'SymbolList[0]': product_name,
            'Country': 'PL',
            'Language': 'en',
        }

        try:
            response = urllib.request.urlopen(client.request('/Products/GetProducts', parameters))
            response_str = response.read().decode('utf-8')
            response_json = json.loads(response_str)

            product = response_json["Data"]["ProductList"][0]
            product_dict = {
                "TME_Name": product["Symbol"],
                "Producer": product["Producer"],
                "Description": product["Description"],
                "MinAmount": int(product["MinAmount"])
            }
            return product_dict

        except urllib.error.URLError as e:
            print(f"API error!: '{e.reason}'")
            return {"Error": "API error."}

    @staticmethod
    def get_product_stock(product_name: str, auth: list, dont_print: bool = True) -> int:
        sleep(0.5)
        if not dont_print:
            print(f"Getting '{product_name}' stock...")
        token = auth[0]
        secret = auth[1]

        client = Client(token, secret)
        parameters = {
            'SymbolList[0]': product_name,
            'Country': 'PL',
            'Language': 'en',
        }

        try:
            response = urllib.request.urlopen(client.request('/Products/GetStocks', parameters))
            response_str = response.read().decode('utf-8')
            response_json = json.loads(response_str)

            product = response_json["Data"]["ProductList"][0]
            stock_amount = int(product["Amount"])
            if not dont_print:
                print(f"Product stock: {stock_amount}")
            return stock_amount

        except urllib.error.URLError as e:
            print(f"API error!: '{e.reason}'")
            return -1

    @staticmethod
    def get_product_price_and_stock(product_name: str, auth: list, product_amount: int, dont_print: bool = True)\
            -> tuple:
        sleep(0.5)
        if not dont_print:
            print(f"Getting '{product_name}' prices and stock...")
        token = auth[0]
        secret = auth[1]

        client = Client(token, secret)
        parameters = {
            'SymbolList[0]': product_name,
            'Country': 'PL',
            'Language': 'en',
            'Currency': 'PLN'
        }

        try:
            response = urllib.request.urlopen(client.request('/Products/GetPricesAndStocks', parameters))
            response_str = response.read().decode('utf-8')
            response_json = json.loads(response_str)

            product = response_json["Data"]["ProductList"][0]
            stock_amount = int(product["Amount"])
            list_of_amounts = product["PriceList"]
            price_per_needed = -2
            for index, price_basket in enumerate(list_of_amounts):
                if index == 0:
                    if int(price_basket["Amount"]) > product_amount:
                        price_per_needed = float(price_basket["PriceValue"]) * 1.23
                        break
                if int(price_basket["Amount"]) > product_amount:
                    continue
                price_per_needed = float(price_basket["PriceValue"]) * 1.23
            if not dont_print:
                print(f"Product stock: {stock_amount}")
                print(f"Product price: {price_per_needed}")
            return stock_amount, price_per_needed

        except urllib.error.URLError as e:
            print(f"API error!: '{e.reason}'")
            return -1, -1

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

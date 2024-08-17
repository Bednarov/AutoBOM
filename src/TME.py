import urllib.request
import urllib.error
import json

from api import Client


class API:
    @staticmethod
    def search_for_product(product_name: str, auth: list) -> dict:
        print(f"Searching for '{product_name}'")
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

            found_component_list = []
            product = response_json["Data"]["ProductList"][0]
            product_dict = {
                "TME_Name": product["Symbol"],
                "Producer": product["Producer"],
                "Description": product["Description"],
                "MinAmount": int(product["MinAmount"])
            }
            return product_dict

        except urllib.error.URLError as e:
            print(e.reason)
            return {"Error": "API error."}

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
            return found_symbols_list

        except urllib.error.URLError as e:
            print(e.reason)
            return []

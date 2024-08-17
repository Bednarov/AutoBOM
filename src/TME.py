import urllib.request
import urllib.error
import json

from api import Client


class API:
    @staticmethod
    def search_for_product(product_name: str, auth: list):
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
            if response_json["Status"] == "OK":
                print(response_json["Data"]["ProductList"])
            else:
                print(response_json)
        except urllib.error.URLError as e:
            print(e.reason)

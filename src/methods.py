import os
import csv
import json
from time import sleep
from enum import Enum

from prototypes import ColumnName, ComponentType, Component, Product
from TME import API


VAT = 1.23


class UserActions(Enum):
    SEARCH = "Search"
    SKIP = "Skip"
    EXIT = "Exit"
    PAGE_UP = "Page up"
    PAGE_DOWN = "Page down"
    MANUAL_SEARCH = "Manual search"
    SELECT = "Select"


class SearchResults(Enum):
    FOUND_NONE = "Not found"
    FOUND_BUT_NOT_IN_STOCK = "Not in stock"
    FOUND_ONE = "Found one"
    FOUND_MULTIPLE = "Found multiple"
    SEARCH_ERROR = "Search error"


class Methods:
    @staticmethod
    def parse_csv(file_path: str) -> list:
        print("> Opening CSV file")
        with open(file_path, newline='', encoding='utf-16') as csvfile:
            reader = csv.reader(csvfile, delimiter='\t', quotechar='|')
            components = []
            for index, row in enumerate(reader):
                if index == 0:
                    continue
                else:
                    new_component_name = None
                    new_component_designators = None
                    new_component_footprint = None
                    new_component_quantity = None
                    new_component_typeof = None
                    for i, element in enumerate(row):
                        if list(ColumnName)[i].value == ColumnName.NAME.value:
                            new_component_name = str(element.strip('"'))
                        elif list(ColumnName)[i].value == ColumnName.DESIGNATOR.value:
                            new_component_designators = element.strip('"').split(",")
                        elif list(ColumnName)[i].value == ColumnName.FOOTPRINT.value:
                            new_component_footprint = str(element.strip('"'))
                        elif list(ColumnName)[i].value == ColumnName.QUANTITY.value:
                            new_component_quantity = int(element.strip('"'))
                    # recognize type
                    designator_str = ""
                    for char in new_component_designators[0]:
                        if not char.isnumeric():
                            designator_str += char
                        else:
                            break
                    for i, typeof in enumerate(list(ComponentType)):
                        if isinstance(typeof.value, list):
                            if designator_str in typeof.value:
                                new_component_typeof = typeof
                        elif designator_str == typeof.value:
                            new_component_typeof = typeof
                    components.append(Component(name=new_component_name, designators=new_component_designators,
                                                footprint=new_component_footprint, quantity=new_component_quantity,
                                                typeof=new_component_typeof))
            print(f"\nParsed {len(components)} different components.")
            sleep(1)
            return components

    @staticmethod
    def input_file_path() -> str:
        while True:
            print("\n> Please input full path to EasyEDA BOM CSV file:")
            file_path = input().replace(os.sep, '/')
            if os.path.exists(file_path):
                print("Path correct.")
                return file_path
            else:
                print("Invalid path. Try again.")

    @staticmethod
    def input_how_many_copies(components: list) -> list:
        while True:
            print("\n> Please input how many copies of the project is needed:")
            user_input = input()
            if user_input.isnumeric() and int(user_input) > 0:
                copies_amount = int(user_input)
                break
            else:
                print("Invalid input.")
        for component in components:
            component.quantity *= copies_amount
        return components

    @staticmethod
    def input_search_skip_exit() -> UserActions:
        print("> Press [enter] to continue, or [s] to skip, [e] to abort:")
        user_input = input()
        if user_input in ["s", "S"]:
            print("Skipping...")
            sleep(1)
            return UserActions.SKIP
        if user_input in ["e", "E"]:
            print("Aborting program.")
            sleep(1)
            return UserActions.EXIT
        return UserActions.SEARCH

    @staticmethod
    def input_not_found_decide(product_name: str) -> UserActions:
        print(f"No product named '{product_name}' was found.")
        while True:
            print("\n> Press [m] for manual search, or [s] to skip, [e] to abort:")
            user_input = input()
            if user_input in ["s", "S"]:
                print("Skipping...")
                sleep(1)
                return UserActions.SKIP
            if user_input in ["e", "E"]:
                print("Aborting program.")
                sleep(1)
                return UserActions.EXIT
            if user_input in ["m", "M"]:
                print("Manual search.")
                sleep(1)
                return UserActions.MANUAL_SEARCH
            print("Invalid input.")

    @staticmethod
    def input_manual_search_not_found() -> UserActions:
        print(f"No product was found.")
        print("> Press [enter] to try again, or [s] to skip, [e] to abort:")
        user_input = input()
        if user_input in ["s", "S"]:
            print("Skipping...")
            sleep(1)
            return UserActions.SKIP
        if user_input in ["e", "E"]:
            print("Aborting program.")
            sleep(1)
            return UserActions.EXIT
        return UserActions.SEARCH

    @staticmethod
    def input_found_multiple_decide(how_many_found: int, how_many_on_screen: int) -> tuple:
        while True:
            if how_many_found > 20:
                print("> Select product to use via [1/2/3...], [n] for next page, [p] for previous page, [m] for "
                      "manual search, or [s] to skip, [e] to abort:")
            else:
                print("> Select product to use via [1/2/3...], [m] for manual search, or [s] to skip, [e] to abort:")
            user_input = input()
            if user_input in ["s", "S"]:
                print("Skipping...")
                sleep(1)
                return UserActions.SKIP, 0
            if user_input in ["e", "E"]:
                print("Aborting program.")
                sleep(1)
                return UserActions.EXIT, 0
            if user_input.isnumeric():
                if 0 < int(user_input) <= how_many_on_screen:
                    return UserActions.SELECT, int(user_input)
            if user_input in ["n", "N"] and how_many_found > 20:
                print("Going to next page.")
                sleep(1)
                return UserActions.PAGE_UP, 0
            if user_input in ["p", "P"] and how_many_found > 20:
                print("Going to previous page.")
                sleep(1)
                return UserActions.PAGE_DOWN, 0
            if user_input in ["m", "M"]:
                print("Manual search.")
                sleep(1)
                return UserActions.MANUAL_SEARCH, 0
            print("Invalid input.\n")

    @staticmethod
    def read_auth_file(save_file_path: str) -> list:
        auth = ["None", "None"]
        print(f"\n> Reading API authentication file...")
        if os.path.exists(os.path.join(save_file_path, "authentication.json")):
            with open(os.path.join(save_file_path, "authentication.json"), 'r') as f:
                config_data = json.load(f)
            auth[0] = config_data["API_KEY"]
            auth[1] = config_data["SECRET"]
            print(f"Authentication file loaded.")
        else:
            print("Authentication file not found.")
            print("> Provide TME API Key:")
            auth[0] = input()
            print("> Provide TME Secret:")
            auth[1] = input()
        return auth

    @staticmethod
    def adjust_component_name(component: Component) -> str:
        if component.typeof is ComponentType.CAPACITOR and component.name[-1] != "F":
            new_name = component.name + "F"
        elif component.typeof is ComponentType.INDUCTOR and component.name[-1] != "H":
            new_name = component.name + "H"
        else:
            new_name = component.name
        return new_name

    @staticmethod
    def is_footprint_smd(component_name: str) -> bool:
        if len(component_name) == 5:
            if component_name[1:].isnumeric():
                if not component_name[0].isnumeric():
                    return True
        return False

    @staticmethod
    def get_search_status(amount_found: int) -> SearchResults:
        if amount_found == 0:
            return SearchResults.FOUND_NONE
        if amount_found == 1:
            return SearchResults.FOUND_ONE
        if amount_found > 1:
            return SearchResults.FOUND_MULTIPLE
        return SearchResults.SEARCH_ERROR

    @staticmethod
    def get_price_for_amount(how_many_needed: int, price_list: list) -> float:
        for price in reversed(price_list):
            if how_many_needed >= price["Amount"]:
                return price["PriceValue"] * VAT
        return -1

    @staticmethod
    def assign_product(component_name: str, product_symbol: str, quantity: int) -> str:
        print(f"> Assigned '{product_symbol}' to '{component_name}'.")
        sleep(1)
        return f"{product_symbol} {quantity}"

    @staticmethod
    def search_for_smd(component_name: str, component_footprint: str, component_needed: int, auth: list, category: str,
                       page: int) -> dict:
        print(f"> Searching for '{component_name + " " + component_footprint}'")
        search_results_raw = API.search_page(component_name + " " + component_footprint, auth, category, page)
        search_status = Methods.get_search_status(search_results_raw["HowManyFound"])
        product_list = []
        if search_status not in [SearchResults.SEARCH_ERROR, SearchResults.FOUND_NONE]:
            for p in search_results_raw["ProductList"]:
                new_product = Product(symbol=p["Symbol"], description=p["Description"], producer=p["Producer"],
                                      min_amount=p["MinAmount"], stock=-1, price=-1)
                product_list.append(new_product)
            symbol_list = []
            for product in product_list:
                symbol_list.append(product.symbol)
            symbol_stock_price_list = API.get_product_price_and_stock_multiple(symbol_list, auth)
            for product in product_list:
                for d in symbol_stock_price_list:
                    if product.symbol == d["Symbol"]:
                        product.stock = d["Stock"]
                        amount = component_needed if component_needed > product.min_amount else product.min_amount
                        product.price = Methods.get_price_for_amount(amount, d["PriceList"])
                        break
            return {
                "Status": search_status,
                "Products": product_list,
                "HowManyFound": search_results_raw["HowManyFound"]
            }
        return {
            "Status": search_status,
            "Products": [],
            "HowManyFound": search_results_raw["HowManyFound"]
        }

    @staticmethod
    def search_for_product(component_name: str, component_needed: int, auth: list, category: str, page: int) -> dict:
        print(f"> Searching for '{component_name}'")
        search_results_raw = API.search_page(component_name, auth, category, page)
        search_status = Methods.get_search_status(search_results_raw["HowManyFound"])
        product_list = []
        if search_status is not SearchResults.SEARCH_ERROR:
            for p in search_results_raw["ProductList"]:
                new_product = Product(symbol=p["Symbol"], description=p["Description"], producer=p["Producer"],
                                      min_amount=p["MinAmount"], stock=-1, price=-1)
                product_list.append(new_product)
            symbol_list = []
            for product in product_list:
                symbol_list.append(product.symbol)
            symbol_stock_price_list = API.get_product_price_and_stock_multiple(symbol_list, auth)
            for product in product_list:
                for d in symbol_stock_price_list:
                    if product.symbol == d["Symbol"]:
                        product.stock = d["Stock"]
                        amount = component_needed if component_needed > product.min_amount else product.min_amount
                        product.price = Methods.get_price_for_amount(amount, d["PriceList"])
                        break
            return {
                "Status": search_status,
                "Products": product_list,
                "HowManyFound": search_results_raw["HowManyFound"]
            }
        return {
            "Status": search_status,
            "Products": [],
            "HowManyFound": search_results_raw["HowManyFound"]
        }

    @staticmethod
    def manual_search(component_name: str, component_needed: int, auth: list, page: int) -> dict:
        print(f"> Manual search for '{component_name}'")
        print("> Input manual search string:")
        search_string = input()
        search_results_raw = API.search_page(search_string, auth, page=page)
        search_status = Methods.get_search_status(search_results_raw["HowManyFound"])
        product_list = []
        if search_status is not SearchResults.SEARCH_ERROR:
            for p in search_results_raw["ProductList"]:
                new_product = Product(symbol=p["Symbol"], description=p["Description"], producer=p["Producer"],
                                      min_amount=p["MinAmount"], stock=-1, price=-1)
                product_list.append(new_product)
            symbol_list = []
            for product in product_list:
                symbol_list.append(product.symbol)
            symbol_stock_price_list = API.get_product_price_and_stock_multiple(symbol_list, auth)
            for product in product_list:
                for d in symbol_stock_price_list:
                    if product.symbol == d["Symbol"]:
                        product.stock = d["Stock"]
                        amount = component_needed if component_needed > product.min_amount else product.min_amount
                        product.price = Methods.get_price_for_amount(amount, d["PriceList"])
                        break
            return {
                "Status": search_status,
                "Products": product_list,
                "HowManyFound": search_results_raw["HowManyFound"]
            }
        return {
            "Status": search_status,
            "Products": [],
            "HowManyFound": search_results_raw["HowManyFound"]
        }

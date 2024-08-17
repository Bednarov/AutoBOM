import sys
import os
import json
import csv
from time import sleep

from prototypes import Component, ComponentType, ColumnName
from TME import API, Categories

# global variables
workdir = os.getcwd()
components = []
purchase_list = []
not_found_list = []
file_path = None  # C:/Users/Grzesiek/Desktop/BOM_Buck-25W-V3-24VCharger_2024-08-07.csv
is_path_incorrect = True
user_input = None

BASIC_TYPES = [
    ComponentType.CAPACITOR,
    ComponentType.RESISTOR,
    ComponentType.INDUCTOR,
    ComponentType.CONNECTOR
]

print("\n\n===== Welcome to AutoBOM! =====")

while is_path_incorrect:
    print("\n> Please input full path to EasyEDA BOM CSV file:")
    file_path = input().replace(os.sep, '/')
    if os.path.exists(file_path):
        is_path_incorrect = False
        print("> Opening CSV file")
    else:
        print("> Invalid path. Try again.")

save_file_path = "/".join(file_path.split("/")[:-1])

with open(file_path, newline='', encoding='utf-16') as csvfile:
    reader = csv.reader(csvfile, delimiter='\t', quotechar='|')
    for index, row in enumerate(reader):
        if index == 0:
            column_names_temp = []
            for i, element in enumerate(row):
                column_names_temp.append(element)
            column_names = dict.fromkeys(column_names_temp)
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

auth = ["None", "None"]
print(f"\n> Reading API authentication file...")
if os.path.exists(os.path.join(save_file_path, "authentication.json")):
    with open(os.path.join(save_file_path, "authentication.json"), 'r') as f:
        config_data = json.load(f)
    auth[0] = config_data["API_KEY"]
    auth[1] = config_data["SECRET"]
    print(f"Authentication file loaded.")
else:
    print("> Authentication file not found.")
    print("> Provide TME API Key:")
    auth[0] = input()
    print("> Provide TME Secret:")
    auth[1] = input()

print("\n> Proceeding with API activity")
all_symbols_list = API.get_all_symbols(auth)
sleep(1)

for index, component in enumerate(components):
    component.printout(index + 1)

    if component.typeof in BASIC_TYPES:
        search_category = Categories[component.typeof.value]
        if component.typeof is ComponentType.CAPACITOR and component.name[-1] != "F":
            new_name = component.name + "F"
        elif component.typeof is ComponentType.INDUCTOR and component.name[-1] != "H":
            new_name = component.name + "H"
        else:
            new_name = component.name
        new_footprint = component.footprint[1:]

        search_result_dicts = API.search_page(new_name + " " + new_footprint, auth, search_category)

        if not search_result_dicts:
            print(f"No product named '{new_name + " " + new_footprint}' was found. Searching again...")
            search_result_dicts = API.search_page(new_name, auth, search_category)
            if not search_result_dicts:
                print(f"No product named '{new_name}' was found.")
                sleep(1)
                not_found_list.append(component.name)
                continue

        print(f"Found {len(search_result_dicts)} matching products.")
        print(f"Checking stocks and prices... 1/{len(search_result_dicts)}", end="")
        list_of_texts = []
        for i, product in enumerate(search_result_dicts):
            print("\r", end="")
            print(f"Checking stocks and prices... {i + 1}/{len(search_result_dicts)}", end="")
            product_stock, product_price = API.get_product_price_and_stock(product['TME_Name'], auth, component.quantity)
            to_buy = component.quantity if component.quantity > product["MinAmount"] else product["MinAmount"]
            list_of_texts.append(f"{i + 1}. {product['TME_Name']}: '{product['Description']}' by {product['Producer']} "
                                 f"=== needed: {component.quantity}, minAmount: {product['MinAmount']}, price: "
                                 f"{product_price:.2f} PLN, total: {product_price * to_buy:.2f} PLN === "
                                 f"stock: {product_stock}")
        print("\nSelect product:")
        for text in list_of_texts:
            print(text)

        print(f"> Select product to use as '{component.name}' component, type selected number or type [s] to skip, "
              f"[e] to abort:")
        user_input = input()
        if user_input in ["e", "E"]:
            print("> Aborting program.")
            sys.exit()
        if user_input in ["s", "S"]:
            print(f"Component '{component.name}' selection aborted.")
            not_found_list.append(component.name)
            continue
        if user_input.isnumeric():
            if int(user_input) < 1 or int(user_input) > len(search_result_dicts):
                print("Invalid selection. Skipping...")
                sleep(1)
                not_found_list.append(component.name)
                continue
            found_product = search_result_dicts[int(user_input) - 1]
            tme_product_text = found_product["TME_Name"]
            tme_min_amount = found_product["MinAmount"]
            if tme_min_amount > component.quantity:
                to_purchase = tme_min_amount
            else:
                to_purchase = component.quantity
            print(f"> Assigned '{tme_product_text}' to '{component.name}'.")
            sleep(1)
            purchase_list.append(f"{tme_product_text} {to_purchase}")
            continue

    print("> Searching for product in all symbols...")
    search_result = list(filter(lambda x: component.name in x, all_symbols_list))

    if not search_result:
        print(f"No product with symbol '{component.name}' was found. Searching again...")
        search_result_dicts = API.search_page(component.name, auth)
        search_result = [x["TME_Name"] for x in search_result_dicts]
        if not search_result:
            print(f"No product named '{component.name}' was found.")
            sleep(1)
            not_found_list.append(component.name)
            continue

    if len(search_result) == 1:
        print("Found 1 matching product.")
        found_product = API.get_specific_product_info(component.name, auth)
        product_stock = API.get_product_stock(component.name, auth)
        if product_stock < component.quantity:
            print(f"Product '{component.name}' not in stock. In stock: {product_stock}, needed: {component.quantity}")
            sleep(1)
            # TODO: Try to search for simmilar ones and present to user
            not_found_list.append(component.name)
            continue
        tme_product_text = found_product["TME_Name"]
        tme_min_amount = found_product["MinAmount"]
        if tme_min_amount > component.quantity:
            to_purchase = tme_min_amount
        else:
            to_purchase = component.quantity
        print(f"> Assigned '{tme_product_text}' to '{component.name}'.")
        sleep(1)
        purchase_list.append(f"{tme_product_text} {to_purchase}")
        continue

    elif len(search_result) > 1:
        print(f"Found {len(search_result)} matching products.")

        print(f"Checking stocks and prices... 1/{len(search_result_dicts)}", end="")
        list_of_texts = []
        for i, product in enumerate(search_result):
            print("\r", end="")
            print(f"Checking stocks and prices... {i + 1}/{len(search_result_dicts)}", end="")
            product_stock, product_price = API.get_product_price_and_stock(product, auth, component.quantity)
            found_product = API.get_specific_product_info(product, auth)
            to_buy = component.quantity if component.quantity > found_product["MinAmount"] else found_product["MinAmount"]
            list_of_texts.append(f"{i + 1}. {found_product['TME_Name']}: '{found_product['Description']}' by "
                                 f"{found_product['Producer']} === needed: {component.quantity}, minAmount: "
                                 f"{found_product['MinAmount']}, price: {product_price:.2f} PLN, total: "
                                 f"{product_price * to_buy:.2f} PLN === stock: {product_stock}")
        print("\nSelect product:")
        for text in list_of_texts:
            print(text)

        print(f"> Select product to use as '{component.name}' component, type selected number or type [s] to skip, "
              f"[e] to abort:")
        user_input = input()
        if user_input in ["e", "E"]:
            print("> Aborting program.")
            sys.exit()
        if user_input in ["s", "S"]:
            print(f"Component '{component.name}' selection aborted.")
            not_found_list.append(component.name)
            continue
        if user_input.isnumeric():
            if int(user_input) < 1 or int(user_input) > len(search_result):
                print("Invalid selection. Skipping...")
                sleep(1)
                not_found_list.append(component.name)
                continue
            selected_name = search_result[int(user_input) - 1]
            found_product = API.get_specific_product_info(selected_name, auth)
            tme_product_text = found_product["TME_Name"]
            tme_min_amount = found_product["MinAmount"]
            if tme_min_amount > component.quantity:
                to_purchase = tme_min_amount
            else:
                to_purchase = component.quantity
            print(f"> Assigned '{tme_product_text}' to '{component.name}'.")
            sleep(1)
            purchase_list.append(f"{tme_product_text} {to_purchase}")
            continue

print("\n> Press [enter] to continue:")
_ = input()

# saving the file lists
if os.path.exists(os.path.join(save_file_path, "components.txt")):
    os.remove(f"{save_file_path}/components.txt")

file = open(os.path.join(save_file_path, "components.txt"), 'w', encoding="utf-8")
for line in purchase_list:
    file.write(line+"\n")
file.close()

if os.path.exists(os.path.join(save_file_path, "not_found.txt")):
    os.remove(f"{save_file_path}/not_found.txt")

file = open(os.path.join(save_file_path, "not_found.txt"), 'w', encoding="utf-8")
for line in not_found_list:
    file.write(line+"\n")
file.close()

print(f"> Purchase list saved to {os.path.join(save_file_path, "components.txt")}")
print(f"> Not Fund list saved to {os.path.join(save_file_path, "not_found.txt")}")

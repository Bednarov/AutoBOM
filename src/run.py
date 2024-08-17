import sys
import os
import json
import csv
from time import sleep

from prototypes import Component, ComponentType, ColumnName
from TME import API

# global variables
workdir = os.getcwd()
components = []
purchase_list = []
not_found_list = []
file_path = None  # C:\Users\Grzesiek\Desktop\BOM_Buck-25W-V3-24VCharger_2024-08-07.csv
is_path_incorrect = True
user_input = None

BASIC_TYPES = [
    ComponentType.CAPACITOR,
    ComponentType.RESISTOR,
    ComponentType.INDUCTOR,
    ComponentType.CONNECTOR
]

print("\n\nWelcome to AutoBOM")

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
            designator_letter = new_component_designators[0][0]
            for i, typeof in enumerate(list(ComponentType)):
                if designator_letter == typeof.value:
                    new_component_typeof = typeof
            components.append(Component(name=new_component_name, designators=new_component_designators,
                                        footprint=new_component_footprint, quantity=new_component_quantity,
                                        typeof=new_component_typeof))

print(f"\nParsed {len(components)} different components.")
print("> Press any key to continue:")
_ = input()

auth = ["None", "None"]
print(f"\n> Reading authentication file...")
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
    if component.typeof in BASIC_TYPES:
        continue  # TODO: handle searching for passive components (get categories -> get category id from name search -> search in category id by param

    component.printout(index + 1)
    print("> Searching for component...")
    search_result = list(filter(lambda x: component.name in x, all_symbols_list))

    if not search_result:
        print(f"No product matching '{component.name}' was found.")
        # TODO: If not in stock or not fount try to research by just a beginning of name
        not_found_list.append(component.name)
        continue

    if len(search_result) == 1:
        print("Found 1 matching component.")
        found_product = API.search_for_product(component.name, auth)
        tme_product_text = found_product["TME_Name"]
        tme_min_amount = found_product["MinAmount"]
        if tme_min_amount > component.quantity:
            to_purchase = tme_min_amount
        else:
            to_purchase = component.quantity
        print(f"> Assigned '{tme_product_text}' to '{component.name}'.")
        purchase_list.append(f"{tme_product_text} {to_purchase}")
        continue

    elif len(search_result) > 1:
        print(f"Found {len(search_result)} matching components:")
        for i, product in enumerate(search_result):
            print(f"{i + 1}. {product}")
        print(f"> Select component to use as '{component.name}' [1/2/3 etc] or press [s] to skip, [e] to abort:")
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
                not_found_list.append(component.name)
                continue
            selected_name = search_result[int(user_input) - 1]
            found_product = API.search_for_product(selected_name, auth)
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

print("\n> Press any key to continue:")
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

import sys
import os
import json
import csv
from prototypes import Component, ComponentType, ColumnName
from TME import API

# global variables
workdir = os.getcwd()
components = []
purchase_list = []
file_path = None  # C:\Users\Grzesiek\Desktop\BOM_Buck-25W-V3-24VCharger_2024-08-07.csv
is_path_incorrect = True
user_input = None
abort_program = False

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

print("\n> Parsed components:")
for index, component in enumerate(components):
    component.printout(index + 1)

print("\n> Please verify the above list. Is it correct? [y/n]:")
user_input = input()

if user_input in ["y", "Y"]:
    print("\n> Proceeding with API activity")

    auth = ["None", "None"]
    print(f"Reading authentication file...")
    if os.path.exists(os.path.join(save_file_path, "authentication.json")):
        with open(os.path.join(save_file_path, "authentication.json"), 'r') as f:
            config_data = json.load(f)
        auth[0] = config_data["API_KEY"]
        auth[1] = config_data["SECRET"]
    else:
        print("> Authentication file not found.")
        print("> Provide TME API Key:")
        auth[0] = input()
        print("> Provide TME Secret:")
        auth[1] = input()

    for index, component in enumerate(components):
        if component.typeof in BASIC_TYPES:
            continue
        component.printout(index + 1)
        print(f"> Press any key to search for this component. "
              f"Press [s] to skip, press [e] to abort:")
        user_input = input()
        if user_input in ["s", "S"]:
            continue
        if user_input in ["e", "E"]:
            abort_program = True
            break
        print("> Searching for component...")

        # search for in api
        API.search_for_product(component.name, auth)

        while True:  # TODO: Handle selecting when multiple found or when nothing found
            print("> Select proper component:") # TODO: FIX
            _ = input()
            tme_product_text = "None"  # TODO: Get proper text
            print(f"Assigned {tme_product_text} to {component.name}")
            print("> Is this correct? [y/n]")
            user_input = input()
            if user_input in ["y", "Y"]:
                break
            print("> Aborted.")
        purchase_list.append(f"{tme_product_text} {component.quantity}")

    if abort_program:
        print("> Aborting program.")
        sys.exit()

    print("> Press any key to continue:")
    _ = input()

    file_content = {
        "Components list": purchase_list
    }
    if os.path.exists(os.path.join(save_file_path, "components.json")):
        os.remove(f"{save_file_path}/components.json")
    with open(os.path.join(save_file_path, "components.json"), "w") as f:
        json.dump(file_content, f, indent=4)
    print(f"> Purchase list saved to {os.path.join(save_file_path, "components.json")}")

else:
    print("> List not correct, aborting...")

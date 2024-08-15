import os
import csv
import json
import sys

from selenium import webdriver

from prototypes import Component, ComponentType, ColumnName
from TME_website import TME, Browser

# global variables
skip_to_browser = False

components = []
purchase_list = []
file_path = None  # C:\Users\Grzesiek\Desktop\BOM_Buck-25W-V3-24VCharger_2024-08-07.csv
is_path_incorrect = True
user_input = [None, None]
abort_program = False


def page_has_loaded(web_driver: webdriver):
    page_state = web_driver.execute_script('return document.readyState;')
    return page_state == 'complete'


print("\n\nWelcome to AutoBOM")

if not skip_to_browser:
    while is_path_incorrect:
        print("\n> Please input full path to EasyEDA BOM CSV file:")
        file_path = input().replace(os.sep, '/')
        if os.path.exists(file_path):
            is_path_incorrect = False
            print("> Opening CSV file")
        else:
            print("> Invalid path. Try again.")

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
                        new_component_name = str(element)
                    elif list(ColumnName)[i].value == ColumnName.DESIGNATOR.value:
                        new_component_designators = element.strip('"').split(",")
                    elif list(ColumnName)[i].value == ColumnName.FOOTPRINT.value:
                        new_component_footprint = str(element)
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
    user_control = input()
else:
    user_control = "Y"

if user_control in ["y", "Y"]:
    print("\n> Proceeding with web browser activity")

    # browser setup
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--disable-search-engine-choice-screen")
    # chrome_options.add_argument("--start-maximized")
    browser = webdriver.Chrome(options=chrome_options)

    search_string_first = "https://www.tme.eu/pl/katalog/?queryPhrase="
    search_string_last = "&productListOrderDir=DESC&onlyInStock=1"
    for index, component in enumerate(components):
        component.printout()
        print("> Press any key to search for this component. Press [s] to skip, press [e] to abort:")
        user_control = input()
        if user_control in ["s", "S"]:
            continue
        if user_control in ["e", "E"]:
            abort_program = True
            break
        print("> Searching for component...")
        skip_component = False
        search_string = search_string_first + component.name + search_string_last
        Browser.search_for_component(browser, component.name)

        while True:
            print("> Select proper component in browser and press any key:")
            _ = input()
            tme_product_text = Browser.get_text(browser, TME.product_symbol())
            print(f"Assigned {tme_product_text} to {component.name}")
            print("> Is this correct? [y/n]")
            user_control = input()
            if user_control in ["y", "Y"]:
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
    save_file_path = "/".join(file_path.split("/")[:-1])
    if os.path.exists(os.path.join(save_file_path, "components.json")):
        os.remove(f"{save_file_path}/components.json")
    # with open('default_config.json', 'w') as f:
    with open(os.path.join(save_file_path, "components.json"), "w") as f:
        json.dump(file_content, f, indent=4)
    print(f"> Purchase list saved to {os.path.join(save_file_path, "components.json")}")

else:
    print("> List not correct, aborting...")

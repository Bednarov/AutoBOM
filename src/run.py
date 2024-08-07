import os
import csv
from selenium import webdriver

from prototypes import Component, ComponentType, ColumnName
from TME_website import TME

# global variables
skip_to_browser = True

components = []
file_path = None  # C:\Users\Grzesiek\Desktop\BOM_Buck-25W-V3-24VCharger_2024-08-07.csv
is_path_incorrect = True
user_input = [None, None]


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
                        new_component_name = element
                    elif list(ColumnName)[i].value == ColumnName.DESIGNATOR.value:
                        new_component_designators = element.strip('"').split(",")
                    elif list(ColumnName)[i].value == ColumnName.FOOTPRINT.value:
                        new_component_footprint = element
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
    chrome_options.add_argument("--start-maximized")
    browser = webdriver.Chrome(options=chrome_options)

    # navigate to the login page
    TME.wait_for_user_to_login(browser)

    # TODO: - if koszyk is not empty, go and empty it
    #  - if koszyk is empty, go into a loop for all components in a list
    #  - loop: for each component - search for name, with available now filter selected and correct footprints
    #  - if found, add it to cart, if found multiple select cheapest, if not found try to find similar
    #  (or save what wasn't found for later)

else:
    print("> List not correct, aborting...")

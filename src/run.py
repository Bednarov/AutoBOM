import sys
import os

from prototypes import Categories, BASIC_TYPES
from TME import API
from methods import Methods, UserActions, SearchResults, SearchType

# global variables
workdir = os.getcwd()
purchase_list = []
not_found_list = []

print("\n\n===== Welcome to AutoBOM! =====")

file_path = Methods.input_file_path()
save_file_path = "/".join(file_path.split("/")[:-1])
components = Methods.parse_csv(file_path)
components = Methods.input_how_many_copies(components)

auth = Methods.read_auth_file(save_file_path)

print("\n> Proceeding with API activity")

for index, component in enumerate(components):
    user_input = None
    search_page = 1
    was_searched = False
    search_type = SearchType.SMD
    user_phrase = ""
    previous_manual_search_string = None
    while True:
        component.printout(index + 1)
        if not was_searched:
            user_input = Methods.input_search_skip_exit()
            if user_input is UserActions.EXIT:
                sys.exit()
            if user_input is UserActions.SKIP:
                not_found_list.append(component.name)
                break
            if component.typeof in BASIC_TYPES:
                search_category = Categories[component.typeof.value]
                new_name = Methods.adjust_component_name(component)
                if Methods.is_footprint_smd(component.footprint):
                    new_footprint = component.footprint[1:]
                else:
                    new_footprint = component.footprint
                search_results = Methods.search_for_smd(new_name, new_footprint, component.quantity, auth,
                                                        search_category, search_page)
                if search_results["Status"] is SearchResults.FOUND_NONE:
                    was_searched = True
                    print(f"No product named '{new_name + " " + new_footprint}' was found. Searching again...")
                    search_type = SearchType.SMD_WIDE
                    search_results = Methods.search_for_product(new_name, component.quantity, auth, search_category,
                                                                search_page)
                    if search_results["Status"] is SearchResults.FOUND_NONE:
                        print(f"No product named '{new_name}' was found. Searching again...")
                        search_type = SearchType.NORMAL
                        search_results = Methods.search_for_product(component.name, component.quantity, auth)
                    if search_results["Status"] is SearchResults.FOUND_NONE:
                        user_input, user_phrase = Methods.input_not_found_decide(new_name)
                        if user_input is UserActions.MANUAL_SEARCH:
                            continue
                        if user_input is UserActions.EXIT:
                            sys.exit()
                        if user_input is UserActions.SKIP:
                            not_found_list.append(component.name)
                            break
                        if user_input is UserActions.ADD_TO_SEARCH:
                            continue
                    if search_results["Status"] is SearchResults.FOUND_ONE:
                        was_searched = True
                        print("Found 1 matching product.")
                        p = search_results["Products"][0]
                        amount = component.quantity if component.quantity >= p.min_amount else p.min_amount
                        new_purchase = Methods.assign_product(component.name, p.symbol, amount)
                        purchase_list.append(new_purchase)
                        break
                    if search_results["Status"] is SearchResults.FOUND_MULTIPLE:
                        was_searched = True
                        print(f"Found {search_results['HowManyFound']} matching products.")
                        for i, p in enumerate(search_results["Products"]):
                            amount = component.quantity if component.quantity >= p.min_amount else p.min_amount
                            p.printout(f"{i + 1}.", component.quantity, amount)
                        user_input, user_selection = Methods.input_found_multiple_decide(
                            search_results["HowManyFound"], len(search_results["Products"]))
                        max_pages = int(search_results["HowManyFound"] / 20) + 1
                        if user_input is UserActions.MANUAL_SEARCH:
                            continue
                        if user_input is UserActions.EXIT:
                            sys.exit()
                        if user_input is UserActions.SKIP:
                            not_found_list.append(component.name)
                            break
                        if user_input is UserActions.PAGE_CHANGE:
                            search_page = user_selection
                            search_page = max_pages if search_page > max_pages else search_page
                            search_page = 1 if search_page < 1 else search_page
                            continue
                        if user_input is UserActions.SELECT:
                            p = search_results["Products"][user_selection - 1]
                            amount = component.quantity if component.quantity >= p.min_amount else p.min_amount
                            new_purchase = Methods.assign_product(component.name, p.symbol, amount)
                            purchase_list.append(new_purchase)
                            break
                        if user_input is UserActions.ADD_TO_SEARCH:
                            user_phrase = user_selection
                            continue

                if search_results["Status"] is SearchResults.FOUND_ONE:
                    was_searched = True
                    print("Found 1 matching product.")
                    p = search_results["Products"][0]
                    amount = component.quantity if component.quantity >= p.min_amount else p.min_amount
                    new_purchase = Methods.assign_product(component.name, p.symbol, amount)
                    purchase_list.append(new_purchase)
                    break
                if search_results["Status"] is SearchResults.FOUND_MULTIPLE:
                    was_searched = True
                    print(f"Found {search_results['HowManyFound']} matching products.")
                    for i, p in enumerate(search_results["Products"]):
                        amount = component.quantity if component.quantity >= p.min_amount else p.min_amount
                        p.printout(f"{i + 1}.", component.quantity, amount)
                    user_input, user_selection = Methods.input_found_multiple_decide(
                        search_results["HowManyFound"], len(search_results["Products"]))
                    max_pages = int(search_results["HowManyFound"] / 20) + 1
                    if user_input is UserActions.MANUAL_SEARCH:
                        continue
                    if user_input is UserActions.EXIT:
                        sys.exit()
                    if user_input is UserActions.SKIP:
                        not_found_list.append(component.name)
                        break
                    if user_input is UserActions.PAGE_CHANGE:
                        search_page = user_selection
                        search_page = max_pages if search_page > max_pages else search_page
                        search_page = 1 if search_page < 1 else search_page
                        continue
                    if user_input is UserActions.SELECT:
                        p = search_results["Products"][user_selection - 1]
                        amount = component.quantity if component.quantity >= p.min_amount else p.min_amount
                        new_purchase = Methods.assign_product(component.name, p.symbol, amount)
                        purchase_list.append(new_purchase)
                        break
                    if user_input is UserActions.ADD_TO_SEARCH:
                        user_phrase = user_selection
                        continue

            else:
                search_results = Methods.search_for_product(component.name, component.quantity, auth)
                if search_results["Status"] is SearchResults.FOUND_NONE:
                    user_input, user_phrase = Methods.input_not_found_decide(component.name)
                    if user_input is UserActions.MANUAL_SEARCH:
                        continue
                    if user_input is UserActions.EXIT:
                        sys.exit()
                    if user_input is UserActions.SKIP:
                        not_found_list.append(component.name)
                        break
                    if user_input is UserActions.ADD_TO_SEARCH:
                        continue
                if search_results["Status"] is SearchResults.FOUND_ONE:
                    print("Found 1 matching product.")
                    p = search_results["Products"][0]
                    amount = component.quantity if component.quantity >= p.min_amount else p.min_amount
                    new_purchase = Methods.assign_product(component.name, p.symbol, amount)
                    purchase_list.append(new_purchase)
                    break
                if search_results["Status"] is SearchResults.FOUND_MULTIPLE:
                    print(f"Found {search_results['HowManyFound']} matching products.")
                    for i, p in enumerate(search_results["Products"]):
                        amount = component.quantity if component.quantity >= p.min_amount else p.min_amount
                        p.printout(f"{i + 1}.", component.quantity, amount)
                    user_input, user_selection = Methods.input_found_multiple_decide(
                        search_results["HowManyFound"], len(search_results["Products"]))
                    max_pages = int(search_results["HowManyFound"] / 20) + 1
                    if user_input is UserActions.MANUAL_SEARCH:
                        continue
                    if user_input is UserActions.EXIT:
                        sys.exit()
                    if user_input is UserActions.SKIP:
                        not_found_list.append(component.name)
                        break
                    if user_input is UserActions.PAGE_CHANGE:
                        search_page = user_selection
                        search_page = max_pages if search_page > max_pages else search_page
                        search_page = 1 if search_page < 1 else search_page
                        continue
                    if user_input is UserActions.SELECT:
                        p = search_results["Products"][user_selection - 1]
                        amount = component.quantity if component.quantity >= p.min_amount else p.min_amount
                        new_purchase = Methods.assign_product(component.name, p.symbol, amount)
                        purchase_list.append(new_purchase)
                        break
                    if user_input is UserActions.ADD_TO_SEARCH:
                        user_phrase = user_selection
                        continue

        else:
            if user_input is UserActions.MANUAL_SEARCH:
                search_type = SearchType.MANUAL
                search_results = Methods.manual_search(component.name, component.quantity, auth, search_page)
                previous_manual_search_string = search_results["SearchString"]
                user_phrase = ""
                if search_results["Status"] is SearchResults.FOUND_NONE:
                    user_input, user_phrase = Methods.input_not_found_decide(component.name)
                    if user_input is UserActions.MANUAL_SEARCH:
                        continue
                    if user_input is UserActions.EXIT:
                        sys.exit()
                    if user_input is UserActions.SKIP:
                        not_found_list.append(component.name)
                        break
                    if user_input is UserActions.ADD_TO_SEARCH:
                        continue
                if search_results["Status"] is SearchResults.FOUND_ONE:
                    print("Found 1 matching product.")
                    p = search_results["Products"][0]
                    amount = component.quantity if component.quantity >= p.min_amount else p.min_amount
                    new_purchase = Methods.assign_product(component.name, p.symbol, amount)
                    purchase_list.append(new_purchase)
                    break
                if search_results["Status"] is SearchResults.FOUND_MULTIPLE:
                    print(f"Found {search_results['HowManyFound']} matching products.")
                    for i, p in enumerate(search_results["Products"]):
                        amount = component.quantity if component.quantity >= p.min_amount else p.min_amount
                        p.printout(f"{i + 1}.", component.quantity, amount)
                    user_input, user_selection = Methods.input_found_multiple_decide(
                        search_results["HowManyFound"], len(search_results["Products"]))
                    max_pages = int(search_results["HowManyFound"] / 20) + 1
                    if user_input is UserActions.MANUAL_SEARCH:
                        continue
                    if user_input is UserActions.EXIT:
                        sys.exit()
                    if user_input is UserActions.SKIP:
                        not_found_list.append(component.name)
                        break
                    if user_input is UserActions.PAGE_CHANGE:
                        search_page = user_selection
                        search_page = max_pages if search_page > max_pages else search_page
                        search_page = 1 if search_page < 1 else search_page
                        continue
                    if user_input is UserActions.SELECT:
                        p = search_results["Products"][user_selection - 1]
                        amount = component.quantity if component.quantity >= p.min_amount else p.min_amount
                        new_purchase = Methods.assign_product(component.name, p.symbol, amount)
                        purchase_list.append(new_purchase)
                        break
                    if user_input is UserActions.ADD_TO_SEARCH:
                        user_phrase = user_selection
                        continue

            if user_input in [UserActions.PAGE_CHANGE, UserActions.ADD_TO_SEARCH]:
                if search_type is SearchType.SMD:
                    search_category = Categories[component.typeof.value]
                    new_name = Methods.adjust_component_name(component)
                    if Methods.is_footprint_smd(component.footprint):
                        new_footprint = component.footprint[1:]
                    else:
                        new_footprint = component.footprint
                    if user_phrase:
                        new_footprint += f" {user_phrase}"
                    search_results = Methods.search_for_smd(new_name, new_footprint, component.quantity, auth,
                                                            search_category, search_page)
                elif search_type is SearchType.SMD_WIDE:
                    search_category = Categories[component.typeof.value]
                    new_name = Methods.adjust_component_name(component)
                    if user_phrase:
                        new_name += f" {user_phrase}"
                    search_results = Methods.search_for_product(new_name, component.quantity, auth, search_category,
                                                                search_page)
                elif search_type is SearchType.NORMAL:
                    if user_phrase:
                        new_name = f"{component.name} {user_phrase}"
                    else:
                        new_name = component.name
                    search_results = Methods.search_for_product(new_name, component.quantity, auth,
                                                                page=search_page)
                else:  # Manual
                    if user_phrase:
                        previous_manual_search_string += f" {user_phrase}"
                        user_phrase = ""
                    search_results = Methods.search_for_product(previous_manual_search_string, component.quantity, auth,
                                                                page=search_page)
                if user_input is UserActions.PAGE_CHANGE:
                    print(f"Found {search_results['HowManyFound']} matching products. Page {search_page}.")
                else:
                    print(f"Found {search_results['HowManyFound']} matching products.")
                for i, p in enumerate(search_results["Products"]):
                    amount = component.quantity if component.quantity >= p.min_amount else p.min_amount
                    p.printout(f"{i + 1}.", component.quantity, amount)
                if user_input is UserActions.PAGE_CHANGE:
                    user_input, user_selection = Methods.input_found_multiple_decide_with_page(
                        len(search_results["Products"]), search_page)
                else:
                    user_input, user_selection = Methods.input_found_multiple_decide(
                        search_results['HowManyFound'], len(search_results["Products"]))
                max_pages = int(search_results["HowManyFound"] / 20) + 1
                if user_input is UserActions.MANUAL_SEARCH:
                    continue
                if user_input is UserActions.EXIT:
                    sys.exit()
                if user_input is UserActions.SKIP:
                    not_found_list.append(component.name)
                    break
                if user_input is UserActions.PAGE_CHANGE:
                    search_page = user_selection
                    search_page = max_pages if search_page > max_pages else search_page
                    search_page = 1 if search_page < 1 else search_page
                    continue
                if user_input is UserActions.SELECT:
                    p = search_results["Products"][user_selection - 1]
                    amount = component.quantity if component.quantity >= p.min_amount else p.min_amount
                    new_purchase = Methods.assign_product(component.name, p.symbol, amount)
                    purchase_list.append(new_purchase)
                    break
                if user_input is UserActions.ADD_TO_SEARCH:
                    user_phrase = user_selection
                    continue

print("\n> Saving product list...")

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

import sys
import os

from prototypes import Categories, BASIC_TYPES
from TME import API
from methods import Methods, UserActions, SearchResults

# C:/Users/Grzesiek/Desktop/BOM_Buck-25W-V3-24VCharger_2024-08-17.csv

# global variables
workdir = os.getcwd()
purchase_list = []
not_found_list = []

print("\n\n===== Welcome to AutoBOM! =====")

# file_path = Methods.input_file_path()  # TODO: DEBUG RESTORE
file_path = "C:/Users/Grzesiek/Desktop/BOM_Buck-25W-V3-24VCharger_2024-08-17.csv"  # TODO: DEBUG DELETE
save_file_path = "/".join(file_path.split("/")[:-1])
components = Methods.parse_csv(file_path)
components = Methods.input_how_many_copies(components)

auth = Methods.read_auth_file(save_file_path)

print("\n> Proceeding with API activity")
all_symbols_list = API.get_all_symbols(auth)

for index, component in enumerate(components):
    user_input = None
    search_page = 1
    was_searched = False
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
                    search_results = Methods.search_for_product(new_name, component.quantity, auth, search_category,
                                                                search_page)
                    if search_results["Status"] is SearchResults.FOUND_NONE:
                        user_input = Methods.input_not_found_decide(new_name)
                        if user_input is UserActions.MANUAL_SEARCH:
                            continue
                        if user_input is UserActions.EXIT:
                            sys.exit()
                        if user_input is UserActions.SKIP:
                            not_found_list.append(component.name)
                            break
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
                            p.printout(f"{i + 1}. '{component.name}'", component.quantity, amount)
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
                        if user_input is UserActions.PAGE_UP:
                            search_page += 1
                            search_page = max_pages if search_page > max_pages else search_page
                            continue
                        if user_input is UserActions.PAGE_DOWN:
                            search_page -= 1
                            search_page = 1 if search_page < 1 else search_page
                            continue
                        if user_input is UserActions.SELECT:
                            p = search_results["Products"][user_selection - 1]
                            amount = component.quantity if component.quantity >= p.min_amount else p.min_amount
                            new_purchase = Methods.assign_product(component.name, p.symbol, amount)
                            purchase_list.append(new_purchase)
                            break

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
                        p.printout(f"{i + 1}. '{component.name}'", component.quantity, amount)
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
                    if user_input is UserActions.PAGE_UP:
                        search_page += 1
                        search_page = max_pages if search_page > max_pages else search_page
                        continue
                    if user_input is UserActions.PAGE_DOWN:
                        search_page -= 1
                        search_page = 1 if search_page < 1 else search_page
                        continue
                    if user_input is UserActions.SELECT:
                        p = search_results["Products"][user_selection - 1]
                        amount = component.quantity if component.quantity >= p.min_amount else p.min_amount
                        new_purchase = Methods.assign_product(component.name, p.symbol, amount)
                        purchase_list.append(new_purchase)
                        break

            # ADD FOR NON_BASIC types

        else:
            if user_input is UserActions.MANUAL_SEARCH:
                search_results = Methods.manual_search(component.name, component.quantity, auth, search_page)
                if search_results["Status"] is SearchResults.FOUND_NONE:
                    user_input = Methods.input_not_found_decide(component.name)
                    if user_input is UserActions.MANUAL_SEARCH:
                        continue
                    if user_input is UserActions.EXIT:
                        sys.exit()
                    if user_input is UserActions.SKIP:
                        not_found_list.append(component.name)
                        break
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
                        p.printout(f"{i + 1}. '{component.name}'", component.quantity, amount)
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
                    if user_input is UserActions.PAGE_UP:
                        search_page += 1
                        search_page = max_pages if search_page > max_pages else search_page
                        continue
                    if user_input is UserActions.PAGE_DOWN:
                        search_page -= 1
                        search_page = 1 if search_page < 1 else search_page
                        continue
                    if user_input is UserActions.SELECT:
                        p = search_results["Products"][user_selection - 1]
                        amount = component.quantity if component.quantity >= p.min_amount else p.min_amount
                        new_purchase = Methods.assign_product(component.name, p.symbol, amount)
                        purchase_list.append(new_purchase)
                        break

            # TODO: ADD FOR PAGE CHANGE

    # OLD METHODS
    """print(f"> Searching for '{new_name + " " + new_footprint}'")
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

    found_new = False
    if not search_result:
        print(f"No product with symbol '{component.name}' was found. Searching again...")
        search_result_dicts = API.search_page(component.name, auth)
        search_result = [x["TME_Name"] for x in search_result_dicts]
        if not search_result:
            print(f"No product named '{component.name}' was found.")
            sleep(1)
            not_found_list.append(component.name)
            continue
        found_new = True

    if len(search_result) == 1:
        print("Found 1 matching product.")
        if found_new:
            found_product = API.get_specific_product_info(search_result[0], auth)
            product_stock = API.get_product_stock(search_result[0], auth)
        else:
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

        amount_to_check = len(search_result)
        print(f"Checking stocks and prices... 1/{amount_to_check}", end="")
        list_of_texts = []
        for i, product in enumerate(search_result):  # TODO: Different stock check method than in upper part
            print("\r", end="")
            print(f"Checking stocks and prices... {i + 1}/{amount_to_check}", end="")
            product_stock, product_price = API.get_product_price_and_stock(product, auth, component.quantity)
            found_product = API.get_specific_product_info(product, auth)
            to_buy = component.quantity if component.quantity > found_product["MinAmount"] else found_product["MinAmount"]
            if product_stock < to_buy:
                search_result.remove(product)
                continue
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
            continue"""

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

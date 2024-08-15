from selenium.common import StaleElementReferenceException, TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from time import sleep


class TME:
    @staticmethod
    def cookie_agree() -> str: return "[id='CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll']"

    @staticmethod
    def search_bar() -> str: return "[name='queryPhrase']"

    @staticmethod
    def search_submit_button() -> str: return "[class*='search-button']"

    @staticmethod
    def login_button() -> str: return "[aria-label='Zaloguj się']"

    @staticmethod
    def login_modal() -> tuple: return "[class*='login-modal__container']", 3

    @staticmethod
    def login_modal_username() -> tuple: return "[class*='input__container'] > input", 1

    @staticmethod
    def login_modal_password() -> tuple: return "[class*='input__container'] > input", 3

    @staticmethod
    def login_modal_submit_button() -> str: return "[data-testid*='submit-button']"

    @staticmethod
    def logout_wrapper() -> str: return "[class*='logout-wrapper']"

    @staticmethod
    def wait_for_user_to_login(driver: WebDriver):
        while True:
            driver.get("https://www.tme.eu/pl/")
            Browser.wait_and_click(driver, TME.cookie_agree(), ignore_exception=True)
            Browser.wait_and_click(driver, TME.login_button())
            Browser.wait_for(driver, TME.login_modal())

            print("\n> Please login to TME. Press enter when done.")
            _ = input()
            if Browser.wait_for(driver, TME.logout_wrapper()) is False and Browser.wait_for(driver, TME.login_button()) is True:
                print("Not logged in. Try again!")
            else:
                print("Login successfull")
                break

    @staticmethod
    def product_symbol() -> str: return "[class='YvvzM']"


class Browser:
    @staticmethod
    def wait_for_page():
        sleep(2)

    @staticmethod
    def find(driver: WebDriver, locator) -> WebElement:
        if isinstance(locator, str):
            found = driver.find_element(By.CSS_SELECTOR, locator)
            return found
        else:
            actual_locator = locator[0]
            which_one = locator[1]
            found = driver.find_element(By.CSS_SELECTOR, actual_locator)
            if isinstance(found, WebElement):
                return found
            elif isinstance(found, list):
                return found[which_one]

    @staticmethod
    def find_ignore_absence(driver: WebDriver, locator):
        if isinstance(locator, str):
            try:
                found = driver.find_element(By.CSS_SELECTOR, locator)
                return found
            except NoSuchElementException:
                return None
        else:
            actual_locator = locator[0]
            which_one = locator[1]
            try:
                found = driver.find_element(By.CSS_SELECTOR, actual_locator)
                if isinstance(found, WebElement):
                    return found
                elif isinstance(found, list):
                    return found[which_one]
            except NoSuchElementException:
                return None

    @staticmethod
    def wait_for(driver: WebDriver, locator) -> bool:
        if isinstance(locator, tuple):
            actual_locator = locator[0]
            which_one = locator[1]
            try:
                WebDriverWait(driver, 5).until(ec.presence_of_element_located((By.CSS_SELECTOR, actual_locator)))
                return True
            except TimeoutException:
                return False
        else:
            try:
                WebDriverWait(driver, 5).until(ec.presence_of_element_located((By.CSS_SELECTOR, locator)))
                return True
            except TimeoutException:
                return False

    @staticmethod
    def wait_and_click(driver: WebDriver, locator, ignore_exception: bool = False) -> None:
        Browser.wait_for_page()
        Browser.wait_for(driver, locator)
        if ignore_exception:
            element = Browser.find_ignore_absence(driver, locator)
            if element:
                element.click()
        else:
            Browser.find(driver, locator).click()

    @staticmethod
    def wait_and_input(driver: WebDriver, locator, input_string: str) -> None:
        Browser.wait_for_page()
        Browser.wait_for(driver, locator)
        Browser.find(driver, locator).send_keys(input_string)

    @staticmethod
    def get_text(driver: WebDriver, locator) -> str:
        Browser.wait_for_page()
        Browser.wait_for(driver, locator)
        found = Browser.find(driver, locator)
        if isinstance(found, WebElement):
            return found.text
        elif isinstance(found, list):
            while True:
                print("\n> Found multiple values for 'TME product name'. Select from below:")
                for index, element in enumerate(found):
                    print(f"{index + 1} - {element.text}")
                user_selection = input()
                if user_selection in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                    user_number = int(user_selection)
                    if user_number <= len(found):
                        break
                print("Invalid input.")
            return found[int(user_selection) - 1]

    @staticmethod
    def search_for_component(driver: WebDriver, component_name: str):
        driver.get("https://www.tme.eu/pl/")
        Browser.wait_and_click(driver, TME.cookie_agree(), ignore_exception=True)
        Browser.wait_and_input(driver, TME.search_bar(), component_name)
        Browser.wait_and_click(driver, TME.search_submit_button())

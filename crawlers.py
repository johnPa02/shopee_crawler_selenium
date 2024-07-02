import json
import os
import time
import pyautogui
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait

load_dotenv()

MAX_WAIT_TIME = 10


def save_to_file(data, filename):
    if type(data) == list:
        data = list(set(data))
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)


class BaseCrawler:
    def __init__(self, headless=False):
        self.driver = None
        self.headless = headless
        # self.username = os.getenv("SHOPEE_USERNAME")
        # self.password = os.getenv("SHOPEE_PASSWORD")
        self.init_driver()

    def init_driver(self):
        options = Options()
        options.headless = self.headless
        # options.add_argument("proxy-server=116.106.105.150:1080")
        options.add_argument(r"--user-data-dir=C:\Users\Windows\AppData\Local\Google\Chrome\User Data\Profile 2")
        self.driver = uc.Chrome(options=options)
        self.driver.set_page_load_timeout(MAX_WAIT_TIME)

    def load_page(self, url):
        self.driver.get(url)

    def scroll_down(self):
        # Scroll down until the next page button is found
        while True:
            self.driver.execute_script("window.scrollBy(0, 720);")
            time.sleep(0.5)
            try:
                self.driver.find_element(
                    "xpath",
                    '//*[@id="main"]/div/div[2]/div/div/div[4]/div[2]/section/ul/li[60]/a')
                break
            except NoSuchElementException:
                pass


class ProductCrawler(BaseCrawler):
    MAX_PRODUCTS = 100
    NUM_PRODUCTS_PER_PAGE = 60

    def __init__(self, headless=False):
        super().__init__(headless)
        self.product_urls = []

    # def login(self):
    #     self.load_page("https://shopee.vn/buyer/login")
    #     try:
    #         username_input = WebDriverWait(self.driver, MAX_WAIT_TIME).until(
    #             EC.presence_of_element_located(
    #                 (By.XPATH, '//*[@id="main"]/div/div[2]/div/div/div/div[2]/div/div[2]/form/div[1]/div[1]/input')))
    #         password_input = self.driver.find_element("xpath",
    #                                                   '//*[@id="main"]/div/div[2]/div/div/div/div[2]/div/div[2]/form/div[2]/div[1]/input')
    #         login_button = self.driver.find_element("xpath",
    #                                                 '//*[@id="main"]/div/div[2]/div/div/div/div[2]/div/div[2]/form/button')
    #         username_input.send_keys(self.username)
    #         password_input.send_keys(self.password)
    #         login_button.click()
    #         time.sleep(5)
    #         print("Login successful")
    #         return True
    #     except NoSuchElementException:
    #         print("Login failed")
    #         self.driver.quit()
    #         return False

    def login_with_cookies(self):
        self.load_page("https://shopee.vn/buyer/login")
        time.sleep(5)
        try:
            with open("cookies.json", 'r') as f:
                cookies = json.load(f)
            for cookie in cookies:
                if "sameSite" not in cookie or cookie["sameSite"] not in ["Strict", "Lax", "None"]:
                    cookie["sameSite"] = "Lax"
                self.driver.add_cookie(cookie)
            self.driver.refresh()
            time.sleep(5)
            print("Logged in with cookies successfully.")
            return True
        except Exception as e:
            print(f"Login with cookies failed: {e}")
            self.driver.quit()
            return False

    def login_with_qr_code(self):
        self.load_page("https://shopee.vn/buyer/login/qr")
        num_tries = 0
        # wait for the user to scan the QR code
        while 'is_from_login=true' not in self.driver.current_url and num_tries < MAX_WAIT_TIME:
            num_tries += 1
            time.sleep(1)

    def open_url_in_new_tab(self, url):
        """
        Open a new tab and simulate manual url entry from the keyboard to avoid bot detection
        :param url:
        :return:
        """
        pyautogui.hotkey('ctrl', 't')
        time.sleep(1)
        pyautogui.write(url)
        pyautogui.press('enter')
        time.sleep(5)
        self.driver.switch_to.window(self.driver.window_handles[-1])

    def find_product_urls(self, category_url):
        """
        Find all product urls in a category
        example: https://shopee.vn/Th%E1%BB%9Di-Trang-Nam-cat.11035567?page=
        :param category_url:
        :return:
        """
        # simulates manual url entry from the keyboard to avoid bot detection
        self.load_page("chrome://newtab")
        time.sleep(2)
        page = 0
        while len(self.product_urls) < self.MAX_PRODUCTS:
            self.open_url_in_new_tab(f"{category_url}{page}")
            self.scroll_down()
            page += 1
            for i in range(1, self.NUM_PRODUCTS_PER_PAGE + 1):
                try:
                    product_element = self.driver.find_element(
                        "xpath",
                        f'//*[@id="main"]/div/div[2]/div/div/div[4]/div[2]/section/ul/li[{i}]/a')
                    self.product_urls.append(product_element.get_attribute('href'))
                    if len(self.product_urls) == self.MAX_PRODUCTS:
                        break
                except NoSuchElementException:
                    break

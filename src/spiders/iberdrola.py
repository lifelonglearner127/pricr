import re
from typing import Tuple, Generator
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from ..libs.engines import SpiderBase


class IberdrolaTexasSpider(SpiderBase):
    name = 'Iberdrola'
    REP_ID = 'IBER'
    base_url = 'https://iberdrolatexas.com/'

    def submit_zipcode(self, zipcode: str):
        zipcode_element = self.wait_until('zipCodeForm_zipCode')
        zipcode_element.send_keys(zipcode)
        zipcode_element.send_keys(Keys.ENTER)

    def get_elements(self) -> Generator[Tuple[WebElement], None, None]:
        elements = self.client.find_elements_by_css_selector(
            'div.EnergyProductCard_content_Ut6R8')
        retries = 0
        while retries < 5 and not elements:
            self.wait_for()
            retries += 1
            elements = self.client.find_elements_by_css_selector(
                'div.EnergyProductCard_content_Ut6R8')
        yield tuple(elements)

    def analyze_element(self, el: WebElement):
        main_client = self.client.current_window_handle

        # product
        product_name = el.find_element_by_xpath('.//div/h2/strong').text

        # term
        term = re.search(r'(\d+(\.\d+)?)', product_name).group()

        # price
        price_element = el.find_element_by_css_selector(
            'h3.Heading_black_k70K9.Heading_center_338zS.Heading_h3_2FwVg'
        )
        price = re.search(r'(\d+(\.\d+)?)', price_element.text).group()

        # download
        # open the modal
        button_element = el.find_element_by_xpath(
            ".//button[contains(@class, 'Link_primary_3KooB')]")
        self.client.execute_script("arguments[0].click();", button_element)

        dialog_element = self.wait_until(
            'Modal_modalBackdrop_2tUY1', by=By.CLASS_NAME)

        link = dialog_element.find_element_by_xpath('.//a')
        link.click()

        self.wait_for(5)
        self.client.switch_to_window(self.client.window_handles[-1])
        download_button_element = self.wait_until(
            "downloadbutton", by=By.CLASS_NAME, timeout=30
        )
        self.client.execute_script(
            "arguments[0].click();", download_button_element)
        self.wait_for(10)
        self.client.close()
        self.client.switch_to.window(main_client)
        self.wait_for(10)

        close_button = dialog_element.find_element_by_xpath('.//button')
        close_button.click()

        return {
            'term': term,
            'price': price,
            'product_name': product_name,
        }

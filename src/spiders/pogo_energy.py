import re
from typing import Tuple, Generator
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from ..libs.engines import SpiderBase


class PogoEnergy(SpiderBase):
    name = 'Pogo Energy'
    REP_ID = 'POGO'
    base_url = 'https://my.pogoenergy.com/enroll'

    def submit_zipcode(self, zipcode: str):
        mat_field_element = self.wait_until("mat-form-field", by=By.TAG_NAME)
        zipcode_element = mat_field_element.find_element_by_id(
            'service_address_id'
        )
        zipcode_element.clear()
        for code in zipcode:
            zipcode_element.send_keys(code)
            self.wait_for(2)

        self.wait_for(3)
        retries = 0
        mat_option_elements = mat_field_element.find_elements_by_xpath(
            './/mat-card/mat-option')

        while not mat_option_elements and retries < 5:
            mat_option_elements = mat_field_element.find_elements_by_xpath(
                './/mat-card/mat-option')
            retries += 1
            self.wait_for()

        mat_option_elements[0].click()
        submit_button_element = self.wait_until("home_next")
        submit_button_element.click()

    def get_elements(self) -> Generator[Tuple[WebElement], None, None]:
        container = self.wait_until('app-plan-details', by=By.TAG_NAME)
        elements = container.find_elements_by_css_selector('div.plan-details')
        retries = 0
        while retries < 5 and not elements:
            self.wait_for(1)
            elements = container.find_elements_by_css_selector(
                'div.plan-details')
            retries += 1
        yield tuple(elements)

    def analyze_element(self, el: WebElement):
        detail_element = el.find_element_by_xpath(".//div[2]")

        # term
        term = 0

        # price
        price_element = el.find_element_by_xpath('.//p[2]')
        price = re.search(r'(\d+(\.\d+)?)', price_element.text).group()

        # product
        product_name = detail_element.find_element_by_xpath('.//p/strong').text

        # download
        dropdown_arrow_element = el.find_element_by_xpath('.//a')
        dropdown_arrow_element.click()
        self.wait_for()

        panel_element = detail_element.find_element_by_css_selector(
            'div.ng-star-inserted'
        )
        retries = 0
        while not panel_element and retries < 0:
            retries += 1
            self.wait_for()
            panel_element = detail_element.find_element_by_css_selector(
                'div.ng-star-inserted'
            )

        link = panel_element.find_element_by_xpath('.//p[2]/a')
        link.click()
        self.wait_for(5)

        return {
            'term': term,
            'price': price,
            'product_name': product_name,
        }

import re
from typing import Tuple, Generator
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from ..libs.engines import SpiderBase


class V247EnergySpider(SpiderBase):
    name = 'V247 Energy'
    REP_ID = 'PLSE'
    base_url = 'https://v247power.com/'

    def submit_zipcode(self, zipcode: str):
        zipcode_element = self.wait_until(
            '//input[@class="zipextr"]',
            by=By.XPATH
        )
        self.wait_for()
        zipcode_element.clear()
        zipcode_element.send_keys(zipcode)
        zipcode_element.send_keys(Keys.ENTER)

    def get_elements(self) -> Generator[Tuple[WebElement], None, None]:
        container = self.wait_until(
            'view-plan-page', by=By.CLASS_NAME)
        elements = container.find_elements_by_class_name('column-popular')
        retries = 0
        while retries < 5 and not elements:
            retries += 1
            elements = container.find_elements_by_class_name('column-popular')
        yield tuple(elements)

    def analyze_element(self, el: WebElement):
        product_element = el.find_element_by_xpath(
            './/div[@class="column-popular-in"]//h4')
        product_name = product_element.text
        match = re.search(r'(\d+)\s+Month', product_name)
        if match:
            term = match.group()
        else:
            term = 1

        price_element = el.find_element_by_xpath(
            './/div[@class="column-popular-in"]/p[2]/span')
        price = re.search(r'(\d+(\.\d+)?)', price_element.text).group()

        efl_download_link_element = el.find_element_by_xpath(
            './/div[@class="column-popular-in"]/ul/li[2]/a')
        efl_download_link_element.click()

        return {
            'term': term,
            'price': price,
            'product_name': product_name,
        }

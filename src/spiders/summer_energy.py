import re
from typing import Tuple, Generator
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from ..libs.engines import SpiderBase


class SummerEnergySpider(SpiderBase):
    name = 'SUMMER ENERGY'
    REP_ID = 'SUMM'
    base_url = 'https://www.summerenergy.com/'

    def submit_zipcode(self, zipcode: str):
        zipcode_element = self.wait_until('ZipCodeData_Zip')
        zipcode_element.clear()
        zipcode_element.send_keys(zipcode)
        zipcode_element.send_keys(Keys.ENTER)

    def get_elements(self) -> Generator[Tuple[WebElement], None, None]:
        container = self.wait_until('table.pricing', By.CSS_SELECTOR)
        elements = container.find_elements_by_css_selector(
            'tbody tr')
        retries = 0
        while retries < 5 and not elements:
            retries += 1
            elements = container.find_elements_by_css_selector(
                'tbody tr')
        yield tuple(elements)

    def analyze_element(self, el: WebElement):
        term_element = el.find_element_by_css_selector(
            'td:nth-child(5)')
        term = term_element.text
        match = re.search(r'(\d+)\s+Months', term)
        if match:
            term = match.groups()[0]
        else:
            raise Exception("Term could not match. (%s)" % term)

        price_element = el.find_element_by_css_selector(
            'td:nth-child(2)')
        price = price_element.text.split('$')[1]

        plan_element = el.find_element_by_css_selector(
            'td:nth-child(1)')
        product_name = plan_element.text

        efl_download_link_element = el.find_element_by_css_selector(
            'td:nth-child(7) > a:nth-child(1)')
        pdf_url = efl_download_link_element.get_attribute('href')
        self.client.get(pdf_url)

        return {
            'term': term,
            'price': price,
            'product_name': product_name,
        }

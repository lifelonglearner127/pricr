import re
from typing import Tuple, Generator, List
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from ..libs.engines import SpiderBase
from ..libs.models import Entry


class TownSquareEnergySpider(SpiderBase):
    name = 'TOWN SQUARE ENERGY '
    REP_ID = 'TOWN'
    base_url = 'https://townsquareenergy.com/'

    def extract(self, zipcode: str) -> List[Entry]:
        self.log("Searching with zip code - %s" % zipcode)
        self.submit_zipcode(zipcode)
        self.hook_after_zipcode_submit()
        for elements in self.get_elements():
            for element in elements:
                entry = self.convert_to_entry(
                    zipcode,
                    self.analyze_element(element)
                )
                self.data.append(entry)

    def submit_zipcode(self, zipcode: str):
        zipcode_element = self.wait_until('zipcode')
        zipcode_element.clear()
        zipcode_element.send_keys(zipcode)
        zipcode_element.send_keys(Keys.ENTER)

    def get_elements(self) -> Generator[Tuple[WebElement], None, None]:
        container = self.wait_until('products')
        elements = container.find_elements_by_css_selector(
            'div.h-container.product')
        retries = 0
        while retries < 5 and not elements:
            retries += 1
            elements = container.find_elements_by_css_selector(
                'div.grid-card div.card')
        yield tuple(elements)

    def analyze_element(self, el: WebElement):
        term_element = el.find_element_by_css_selector(
            'div.h-term-description')
        term = term_element.text
        match = re.search(r'(\d+)\s+MONTHS', term)
        if match:
            term = match.groups()[0]
        else:
            raise Exception("Term could not match. (%s)" % term)

        price_element = el.find_element_by_css_selector(
            'div.h-rate-value')
        price = price_element.text

        plan_element = el.find_element_by_css_selector(
            'div.h-terms-title')
        product_name = plan_element.text

        return {
            'term': term,
            'price': price,
            'product_name': product_name,
        }

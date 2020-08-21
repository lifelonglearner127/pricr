import re
from typing import Tuple, Generator, List
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from ..libs.engines import SpiderBase
from ..libs.models import Entry


class ClearviewEnergySpider(SpiderBase):
    name = 'CLEARVIEW ENERGY'
    REP_ID = 'CLEAR'
    base_url = 'https://www.clearviewenergy.com/'

    def extract(self, zipcode: str) -> List[Entry]:
        self.log("Searching with zip code - %s" % zipcode)
        self.submit_zipcode(zipcode)
        self.hook_after_zipcode_submit()
        for elements in self.get_elements():
            for element in elements:
                entry = self.convert_to_entry(
                    zipcode, self.analyze_element(element))
                self.data.append(entry)

    def submit_zipcode(self, zipcode: str):
        zipcode_element = self.wait_until(
            '//input[@name="inputzipcode"]',
            By.XPATH
        )
        zipcode_element.clear()
        zipcode_element.send_keys(zipcode)
        zipcode_element.send_keys(Keys.ENTER)

    def get_elements(self) -> Generator[Tuple[WebElement], None, None]:
        container = self.wait_until(
            'div#rates > section#pricing', By.CSS_SELECTOR)
        elements = container.find_elements_by_css_selector(
            'div.row div.pricing')
        retries = 0
        while retries < 5 and not elements:
            retries += 1
            elements = container.find_elements_by_css_selector(
                'div.row div.pricing')
        yield tuple(elements)

    def analyze_element(self, el: WebElement):
        term_element = el.find_element_by_css_selector(
            'ul.options > li:last-child')
        term = term_element.text.replace('Terms: ', '')
        match = re.search(r'(\d+)\s+Months', term)
        if match:
            term = match.groups()[0]
        elif term == 'End-of-Year':
            term = '12'
        elif term == 'Month-to-month':
            term = '1'
        else:
            raise Exception("Term could not match. (%s)" % term)

        price_element = el.find_element_by_css_selector(
            'div.price')
        price = price_element.text.split("¢")[0]

        plan_element = el.find_element_by_css_selector(
            'div.title')
        product_name = plan_element.text

        # efl_download_link_element = el.find_element_by_css_selector(
        #     'div.card-body.plan-box div.gridPlanLinks span.efl_link a')
        # efl_download_link_element.click()

        return {
            'term': term,
            'price': price,
            'product_name': product_name,
        }

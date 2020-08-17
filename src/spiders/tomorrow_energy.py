import re
from typing import Tuple, Generator, Optional
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ..libs.engines import SpiderBase


class TomorrowEnergySpider(SpiderBase):
    name = 'TOMORROW ENERGY'
    REP_ID = 'TOM'
    base_url = 'https://tomorrowenergy.com/'

    def submit_zipcode(self, zipcode: str):
        zipcode_element = self.wait_until(
            'form#top-homepage-zip-widget input.input-field.zip',
            By.CSS_SELECTOR
        )
        zipcode_element.clear()
        zipcode_element.send_keys(zipcode)
        zipcode_element.send_keys(Keys.ENTER)

    def hook_after_zipcode_submit(self):
        self.wait_until_invisible('large-loader')

    def get_elements(self) -> Generator[Tuple[WebElement], None, None]:
        self.wait_until_invisible('large-loader')
        container = self.wait_until('energy-rates-container', By.CLASS_NAME)
        elements = container.find_elements_by_css_selector(
            'div.rate-plans-container div.rate-card')
        retries = 0
        while retries < 5 and not elements:
            retries += 1
            elements = container.find_elements_by_css_selector(
                'div.rate-plans-container div.rate-card')
        yield tuple(elements)

    def analyze_element(self, el: WebElement):
        term_element = el.find_element_by_css_selector(
            'div.rate-wrapper > ul.tabs-block ~ div.tabs-wrapper ' +
            'div.tab-block.active div.term-block div.term, ' +
            'div.rate-wrapper > ul.tabs-block.hidden ~ div.tabs-wrapper ' +
            'div.tab-block div.term-block div.term'
            )

        term = term_element.text
        match = re.search(r'(\d+)\s+MONTH', term)
        if match:
            term = match.groups()[0]
        else:
            raise Exception("Term could not match. (%s)" % term)

        price_element = el.find_element_by_css_selector(
            'div.rate-wrapper > ul.tabs-block ~ div.tabs-wrapper ' +
            'div.tab-block.active div.price-block span.amount, ' +
            'div.rate-wrapper > ul.tabs-block.hidden ~ div.tabs-wrapper ' +
            'div.tab-block div.price-block span.amount'
            )

        price = price_element.text

        plan_element = el.find_element_by_css_selector(
            'div.card-header div.name')
        product_name = plan_element.text

        efl_link_element = el.find_element_by_css_selector(
            'div.rate-wrapper > div.tabs-wrapper ' +
            'div.full-plan-details div.plan-documents ' +
            'ul.links li.rate-plan-summary')
        self.client.get(
            efl_link_element.get_attribute('data-summary-url'))

        return {
            'term': term,
            'price': price,
            'product_name': product_name,
        }

    def wait_until_invisible(
        self,
        identifier: str,
        by: str = By.ID,
        timeout: int = 15
    ) -> Optional[WebElement]:
        return WebDriverWait(
            self.client, timeout).until(
                EC.invisibility_of_element_located((by, identifier)))

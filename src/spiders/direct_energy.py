import re
from typing import Tuple, Generator
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from ..libs.engines import SpiderBase


class DirectEnergySpider(SpiderBase):
    name = 'Direct Energy'
    REP_ID = 'DE'
    base_url = 'https://www.directenergy.com/'

    def submit_zipcode(self, zipcode: str):
        zipcode_element = self.client.find_element_by_xpath(
            '//div[@id="left-initial"]//form//input[@name="zipcode"]')
        zipcode_element.clear()
        zipcode_element.send_keys(zipcode)
        zipcode_element.send_keys(Keys.ENTER)

    def get_elements(self) -> Generator[Tuple[WebElement], None, None]:
        container = self.wait_until('eplans')
        elements = container.find_elements_by_css_selector(
            'div.grid-card div.card')
        retries = 0
        while retries < 5 or not elements:
            retries += 1
            elements = container.find_elements_by_css_selector(
                'div.grid-card div.card')
        yield tuple(elements)

    def analyze_element(self, el: WebElement):
        term_element = el.find_element_by_css_selector(
            'div.grid-card-header div.col.grid-month')
        term = term_element.text
        match = re.search(r'(\d+)\s+Month', term)
        if match:
            term = match.groups()[0]
        else:
            raise Exception("Term could not match. (%s)" % term)

        price_element = el.find_element_by_css_selector(
            'div.rate_container span.rate_amount')
        price = price_element.text

        plan_element = el.find_element_by_css_selector(
            'div.card-body.plan-box div.grid-planName')
        product_name = plan_element.text

        efl_download_link_element = el.find_element_by_css_selector(
            'div.card-body.plan-box div.gridPlanLinks span.efl_link a')
        efl_download_link_element.click()

        return {
            'term': term,
            'price': price,
            'product_name': product_name,
        }

import re
from typing import Generator, Dict, List
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from ..libs.engines import SpiderBase
from ..libs.models import Entry
import time


class APGESpider(SpiderBase):
    name = 'APGE'
    REP_ID = 'APGE'
    base_url = 'https://enroll.apge.com/'

    def submit_zipcode(self, zipcode: str):
        self.wait_for(5)
        try:
            zipcode_element = self.wait_until(
                '//input[@name="collect-zip-code-zip-code"]', By.XPATH)
        except Exception:
            zipcode_element = self.wait_until(
                '//input[@name="collect-zip-code-zip-code"]', By.XPATH)
        # zipcode_element = self.client.find_element_by_xpath(
        #     '//div[@id="left-initial"]//form//input[@name="zipcode"]')
        zipcode_element.clear()
        zipcode_element.send_keys(zipcode)
        zipcode_element.send_keys(Keys.ENTER)

    def extract(self, zipcode: str) -> List[Entry]:
        self.log("Searching with zip code - %s" % zipcode)
        self.submit_zipcode(zipcode)
        self.hook_after_zipcode_submit()
        for elements in self.get_elements():
            for ind, element in enumerate(elements.get('elements', [])):
                entry = self.convert_to_entry(
                    zipcode,
                    self.analyze_element(
                        element,
                        elements.get('details', [])[ind])
                )
                self.log("Downloading for <%s>..." % entry.product_name)
                if self.wait_until_download_finish():
                    entry.filename = self.rename_downloaded(
                        zipcode,
                        "{}-{}".format(entry.product_name, int(time.time()))
                    )
                self.data.append(entry)

    def hook_after_zipcode_submit(self):
        self.wait_until('choose-offer')

    def get_elements(
        self
    ) -> Generator[Dict[WebElement, WebElement], None, None]:
        container = self.client.find_element_by_css_selector(
            'form#choose-offer > div.list-group'
        )
        elements = container.find_elements_by_xpath(
            'div[@data-bind="css: rowColor"]' +
            '[contains(@class, "list-group-item")]')
        details = container.find_elements_by_xpath(
            'div[@data-bind="fadeVisible: expanded()"]' +
            '[contains(@class, "list-group-item")]')
        retries = 0
        while retries < 5 and (not elements or not details):
            retries += 1
            if not elements:
                elements = container.find_elements_by_xpath(
                    'div[@data-bind="css: rowColor"]' +
                    '[contains(@class, "list-group-item")]')
            elif not details:
                details = container.find_elements_by_xpath(
                    'div[@data-bind="fadeVisible: expanded()"]' +
                    '[contains(@class, "list-group-item")]')
        yield {'elements': elements, 'details': details}

    def analyze_element(self, el: WebElement, el_detail: WebElement):
        el.click()
        term_element = el_detail.find_element_by_css_selector(
            'div.row > div.col-sm-4 > div.list-group' +
            ' > span.list-group-item:nth-child(1) > span:nth-child(2)')
        term = term_element.text

        price_element = el.find_element_by_css_selector(
            'div.row > div.price-col span.price')
        price = price_element.text.split('¢')[0]

        plan_element = el.find_element_by_css_selector(
            'div.row > div.offer-col span.offer-name')
        product_name = plan_element.text

        efl_download_link_element = el_detail.find_element_by_css_selector(
            'div.row > div.col-sm-8 > div.list-group' +
            ' > span.list-group-item:nth-child(2) > span.pull-right' +
            ' > a')
        efl_download_link_element.click()

        return {
            'term': term,
            'price': price,
            'product_name': product_name,
        }

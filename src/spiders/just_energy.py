import re
from typing import Tuple, Generator
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from ..libs.engines import SpiderBase
from time import sleep


class JustEnergySpider(SpiderBase):
    name = 'Just Energy'
    REP_ID = 'JE'
    base_url = 'https://www.justenergy.com/'

    def submit_zipcode(self, zipcode: str):
        zipcode_element = self.client.find_element_by_xpath(
            '//form//input[@id="zip"]')
        zipcode_element.clear()
        zipcode_element.send_keys(zipcode)
        zipcode_element.send_keys(Keys.ENTER)

    def get_elements(self) -> Generator[Tuple[WebElement], None, None]:
        container = self.wait_until('product-rows', By.CLASS_NAME)
        elements = container.find_elements_by_xpath(
            '//app-product-row//div[contains(@class, "product-list-item-v2")]//div[contains(@class, "row")][contains(@class, "tx-title-price-wrapper")][not(contains(@style, "display:none"))]')
        retries = 0
        while retries < 5 and not elements:
            retries += 1
            elements = container.find_elements_by_xpath(
            '//app-product-row//div[contains(@class, "product-list-item-v2")]//div[contains(@class, "row")][contains(@class, "tx-title-price-wrapper")][not(contains(@style, "display:none"))]')
        yield tuple(elements)

    def analyze_element(self, el: WebElement):
        term_element = el.find_element_by_css_selector(
            'div.tx-terms p.plan-term-type')
        term = term_element.text
        match = re.search(r'(\d+)\s+Month', term)
        if match:
            term = match.groups()[0]
        else:
            raise Exception("Term could not match. (%s)" % term)

        price_element = el.find_element_by_css_selector(
            'div.column-price div.price span.currency-unit')
        price = price_element.text.split('¢')[0]

        plan_element = el.find_element_by_css_selector(
            'div.column-title > h4')
        product_name = plan_element.text

        view_detail_button = el.find_element_by_class_name("tx-view-details-btn")
        view_detail_button.click()

        efl_download_modal_button = el.find_element_by_xpath('//a[@class="plan-documents"]')
        efl_download_modal_button.click()

        efl_download_btn = self.wait_until("//div[contains(@class, 'modal-dialog')]//div[@class='text-center']/a", By.XPATH)
        efl_download_btn.click()

        efl_download_modal = self.client.find_element_by_css_selector('div.modal-dialog div.modal-footer button')
        efl_download_modal.click()
        sleep(1)
        view_detail_button.click()

        # efl_download_link_element = el.find_element_by_css_selector(
        #     'div.card-body.plan-box div.gridPlanLinks span.efl_link a')
        # efl_download_link_element.click()

        return {
            'term': term,
            'price': price,
            'product_name': product_name,
        }

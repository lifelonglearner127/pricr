import re
from typing import Tuple, Generator
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from ..libs.engines import SpiderBase


class GexaEnergySpider(SpiderBase):
    name = 'GEXAEnergy'
    REP_ID = 'GEXA'
    base_url = 'https://newenroll.gexaenergy.com/?refid=1DEFAULT'

    def __wait_until_document_ready(self):
        retries, MAX_RETRIES = 0, 12
        loading = self.client.find_element_by_id('loadingmessage')
        while retries < MAX_RETRIES and loading.is_displayed():
            retries += 1
            self.wait_for()
        self.wait_for()

    def submit_zipcode(self, zipcode: str):
        zipcode_element = self.wait_until(
            '//div[@id="myAddressZipModal2"]//input[@id="txtZipCode3"]',
            by=By.XPATH
        )
        zipcode_element.clear()
        zipcode_element.send_keys(zipcode)

        zipcode_submit = self.client.find_element_by_xpath(
            '//div[@id="myAddressZipModal2"]//input[@id="btAddress2"]')
        zipcode_submit.click()
        self.__wait_until_document_ready()

    def hook_after_zipcode_submit(self):
        """Switch to show all the plans
        """
        self.execute_javascript("showTabs('Display All')")
        self.execute_javascript("GetProductsAccordingRates(1000)")
        self.__wait_until_document_ready()

    def get_elements(self) -> Generator[Tuple[WebElement], None, None]:
        elements = self.client.find_elements_by_css_selector(
            'div#divInfo div.container>div>div.row.text-center')
        yield tuple(elements[1:])

    def analyze_element(self, el: WebElement):
        self.wait_until(
            'div#divInfo div.container>div>div.row.text-center ' +
            'div.plan_price_element span.plan_price_value',
            by=By.CSS_SELECTOR
        )
        price_element = el.find_element_by_css_selector(
            'div.plan_price_element span.plan_price_value')
        price = price_element.text

        # Popping up learn more details
        learn_more_link = el.find_element_by_css_selector(
            'span.learn_more_item_text')
        learn_more_link.click()
        self.__wait_until_document_ready()

        modal = self.client.find_element_by_id('ProductDetailInfo')
        product_name = self.wait_until('div#ProductDetailInfo h3', by=By.CSS_SELECTOR).text

        term_element = modal.find_elements_by_css_selector('ul li.mb-2')[0]
        raw_text = term_element.text
        term = re.search(r'Term\s+:\s+(\d+)\s+months', raw_text).groups()[0]

        efl_download_link_element = modal.find_elements_by_css_selector(
            'a.learn_more_item_text')[0]
        efl_download_link_element.click()
        close_button = self.wait_until(
            'div#ProductDetails div.modal-content button.close',
            by=By.CSS_SELECTOR
        )
        close_button.click()
        self.__wait_until_document_ready()

        return {
            'term': term,
            'price': price,
            'product_name': product_name,
        }

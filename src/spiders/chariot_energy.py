import re
from typing import Tuple, Generator
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from ..libs.engines import SpiderBase


class ChariotEnergySpider(SpiderBase):
    name = 'Chariot Energy'
    REP_ID = 'CHAR'
    base_url = 'https://chariotenergy.com/'

    def submit_zipcode(self, zipcode: str):
        zipcode_element = self.client.find_element_by_xpath(
            '//div[@class="banner-form animate2 six"]//form//input[@class="hpf-zipcode"]')
        zipcode_element.clear()
        zipcode_element.send_keys(zipcode)
        zipcode_element.send_keys(Keys.ENTER)

    def hook_after_zipcode_submit(self):
        """Click button before retrieving the elements
        """
        all_products_button = self.wait_until(
            'div.zipcodechildiv div.featurebottom a.approductsbtn',
            by=By.CSS_SELECTOR)
        self.wait_for()
        all_products_button.click()

    def __get_elements_per_page(self) -> Tuple[WebElement]:
        container = self.wait_until('DivProducts')
        self.wait_for()
        elements = container.find_elements_by_css_selector(
            'div.fearturedivcenter div.planbox')

        retries = 0
        while retries < 5 and not elements:
            retries += 1
            elements = container.find_elements_by_css_selector(
                'div.fearturedivcenter div.planbox')
        return tuple(elements)

    def __get_next_page_button(self) -> WebElement:
        next_btn = self.wait_until(
            '#featuredplandiv div.k-floatwrap span.k-i-arrow-e',
            by=By.CSS_SELECTOR)
        classes = next_btn.find_element_by_xpath(
            '..').get_attribute('class').split()
        return None if 'k-state-disabled' in classes else next_btn

    def get_elements(self) -> Generator[Tuple[WebElement], None, None]:
        elements = self.__get_elements_per_page()
        yield elements

        next_btn = self.__get_next_page_button()
        while next_btn:
            next_btn.click()
            next_btn = self.__get_next_page_button()
            yield self.__get_elements_per_page()

    def analyze_element(self, el: WebElement):
        self.wait_for()

        price_element = el.find_element_by_xpath(
            './/p[@class="planprice"]')
        price = re.search(r'(\d+(\.\d+)?)', price_element.text).group()

        plan_element = el.find_element_by_xpath(
            './/p[@class="planname"]')
        product_name = plan_element.text

        term = product_name.split(' ')[1]

        efl_download_link_element = el.find_element_by_xpath(
            './/div[@class="planfiles"]//a')
        efl_download_link_element.click()
        self.wait_for()

        return {
            'term': term,
            'price': price,
            'product_name': product_name,
        }

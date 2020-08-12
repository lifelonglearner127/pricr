import re
from typing import Tuple, Generator
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from ..libs.engines import SpiderBase


class ChariotEnergySpider(SpiderBase):
    name = 'ChariotEnergy'
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
        container = self.wait_until('DivFeaturedPlans')
        self.wait_for()
        add_prod_btn = container.find_element_by_xpath(
            '//div[@class="featurebottom"]//a[@class="approductsbtn"]'
        )
        add_prod_btn.click()

    def __get_elements_per_page(self) -> Tuple[WebElement]:
        container = self.wait_until('planDiv')
        elements = container.find_elements_by_css_selector(
            'div.fearturedivcenter div.planbox')
        retries = 0
        while retries < 5 and not elements:
            retries += 1
            elements = container.find_elements_by_css_selector(
                'div.fearturedivcenter div.planbox')
        return tuple(elements)

    def __get_next_page_button(self) -> WebElement:
        container = self.wait_until('featuredplandiv')
        next_btn = container.find_element_by_css_selector(
            'div.k-floatwrap span.k-i-arrow-e'
        )
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
        price_element = el.find_element_by_css_selector(
            'div.planbox p.planprice')
        price = re.search(r'(\d+(\.\d+)?)', price_element.text).group()

        plan_element = el.find_element_by_css_selector(
            'div.planbox p.planname')
        product_name = plan_element.text

        term = product_name.split(' ')[1]

        efl_download_link_element = el.find_element_by_css_selector(
            'div.planbox div.planfiles a')
        efl_download_link_element.click()

        return {
            'term': term,
            'price': price,
            'product_name': product_name,
        }

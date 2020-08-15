import re
from typing import Tuple, Generator
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from ..libs.engines import SpiderBase


class GRIDEnergySpider(SpiderBase):
    name = 'GRID Energy'
    REP_ID = 'GRID'
    base_url = 'https://grid-enroll.smartgridcis.net/'

    def submit_zipcode(self, zipcode: str):
        zipcode_element = self.wait_until(
            '//input[@name="zip"]',
            by=By.XPATH)
        zipcode_element.clear()
        zipcode_element.send_keys(zipcode)
        submit_btn = self.client.find_element_by_tag_name('button')
        submit_btn.click()

    def get_elements(self) -> Generator[Tuple[WebElement], None, None]:
        container = self.wait_until(
            '//section[@class="content-section"]', by=By.XPATH)
        elements = container.find_elements_by_class_name('columns')
        retries = 0
        while retries < 5 and not elements:
            self.wait_for(2)
            retries += 1
            elements = container.find_elements_by_class_name('columns')
        yield tuple(elements)
    
    def analyze_element(self, el: WebElement):
        plan_element = el.find_element_by_xpath('.//div[@class="price"]/div')
        product_name = plan_element.text
        match = re.search(r'\b\d+\b', product_name)
        if match:
            term = match.group()
        else:
            term = 1
        price_element = el.find_element_by_xpath(
            './/div[@class="price"]/div[2]')
        price = re.search(r'(\d+(\.\d+)?)', price_element.text).group()

        # Popping up learn more details
        detail_btm = el.find_element_by_xpath(
            './/div[@class="price"]//span/button')
        self.client.execute_script("arguments[0].click();", detail_btm)

        modal = self.wait_until(
            '//div[@class="modal-content"]',
            by=By.XPATH
        )
        efl_element = modal.find_element_by_xpath(
            '//ul[@class="free-night-ul"]/li[1]/a[1]')
        self.client.execute_script("arguments[0].click();", efl_element)
        self.wait_for(2)
        close_btn = modal.find_element_by_xpath('//div[@class="modal-footer"]/button')
        self.client.execute_script("arguments[0].click();", close_btn)

        return {
            'term': term,
            'price': price,
            'product_name': product_name,
        }

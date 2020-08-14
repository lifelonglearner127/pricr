import re
from typing import Tuple, Generator
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from ..libs.engines import SpiderBase


class SparkEnergySpider(SpiderBase):
    name = 'Spark Energy'
    REP_ID = 'SPRK'
    base_url = 'https://www.sparkenergy.com/products-and-services/'

    def submit_zipcode(self, zipcode: str):
        zipcode_element = self.wait_until('ZipCode')
        zipcode_element.clear()
        zipcode_element.send_keys(zipcode)
        zipcode_element.send_keys(Keys.ENTER)

    def get_elements(self) -> Generator[Tuple[WebElement], None, None]:
        container = self.wait_until('//div[@class="site-main"]', by=By.XPATH)
        elements = container.find_elements_by_class_name('rate-item')
        retries = 0
        while retries < 5 and not elements:
            retries += 1
            elements = container.find_elements_by_class_name('rate-item')
        yield tuple(elements)
    
    def analyze_element(self, el: WebElement):
        term_element = el.find_element_by_xpath(
            './/div[@class="row"]/div[1]/span')
        match = re.search(r'\b\d+\b', term_element.text)
        if match:
            term = match.group()
        else:
            term = 1
        self.wait_for()
        
        plan_element = el.find_element_by_xpath(
            './/div[@id="product-left"]/h2')
        product_name = plan_element.text

        # Popping up learn more details
        detail_link = el.find_element_by_xpath(
            './/div[@class="row"]/div[3]/a')
        self.client.execute_script("arguments[0].click();", detail_link)
        price_element = el.find_element_by_xpath(
            './/div[@id="product-right"]//h1')
        price = re.search(r'(\d+(\.\d+)?)', price_element.text).group()

        efl_element = el.find_element_by_xpath(
            './/div[@id="product-details-right"]/ul/li[1]/a')
        self.client.execute_script("arguments[0].click();", efl_element)
        
        return {
            'term': term,
            'price': price,
            'product_name': product_name,
        }

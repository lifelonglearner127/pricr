import re
from typing import Tuple, Generator
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from ..libs.engines import SpiderBase


class ThinkEnergySpider(SpiderBase):
    name = 'Think Energy'
    REP_ID = 'THINK'
    base_url = 'https://www.mythinkenergy.com/'

    def submit_zipcode(self, zipcode: str):
        zipcode_element = self.wait_until('zipCodeInput')
        zipcode_element.clear()
        zipcode_element.send_keys(zipcode)
        zipcode_element.send_keys(Keys.ENTER)

    def get_elements(self) -> Generator[Tuple[WebElement], None, None]:
        container = self.wait_until(
            '//div[@class="prices-plans-container"]', by=By.XPATH)
        elements = container.find_elements_by_class_name('rates-container')
        retries = 0
        while retries < 5 and not elements:
            retries += 1
            elements = container.find_elements_by_class_name('rates-container')
        yield tuple(elements)

    def __download_pdf(self, url: str, xpath: str):
        main_client = self.client.current_window_handle
        self.client.execute_script("window.open('');")
        self.client.switch_to_window(self.client.window_handles[-1])
        self.client.get(url)
        # element = self.client.find_element_by_xpath(xpath)
        # pdf_url = element.get_attribute('src')
        # self.client.get(pdf_url)
        self.wait_for(3)
        self.client.close()
        self.client.switch_to.window(main_client)
        self.wait_for()
        return self.client
    
    def analyze_element(self, el: WebElement):
        term_element = el.find_element_by_xpath(
            './/div[@class="term-description"]')
        match = re.search(r'\b\d+\b', term_element.text)
        if match:
            term = match.group()
        else:
            term = 1
        self.wait_for()
        
        plan_element = el.find_element_by_class_name('description-title ')
        product_name = plan_element.text

        price_element = el.find_element_by_xpath(
            './/div[@class="rate-price"]/div[2]')
        price = re.search(r'(\d+(\.\d+)?)', price_element.text).group()

        # Popping up learn more details
        detail_link = el.find_element_by_xpath(
            './/a[@class="detailsButton"]')
        self.client.execute_script("arguments[0].click();", detail_link)
        
        efl_element = el.find_element_by_xpath(
            './/div[@class="planInfoHolder"]//a[1]')
        efl_url = efl_element.get_attribute('href')
        self.__download_pdf(efl_url, '//embed')
        
        return {
            'term': term,
            'price': price,
            'product_name': product_name,
        }

import re
from typing import Tuple, Generator
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from ..libs.engines import SpiderBase


class GreenMountEnergySpider(SpiderBase):
    name = 'Green Mountain Energy'
    REP_ID = 'GME'
    base_url = 'https://www.greenmountainenergy.com/'

    def submit_zipcode(self, zipcode: str):
        self.wait_for(3)
        zipcode_element = self.wait_until(
            '//div[@class="input-wrapper"]//input[@class="search zip-code"]',
            by=By.XPATH
        )
        zipcode_element.clear()
        zipcode_element.send_keys(zipcode)
        zipcode_element.send_keys(Keys.ENTER)

    def get_elements(self) -> Generator[Tuple[WebElement], None, None]:
        self.wait_for(3)
        self.__is_element_exist('mcx_invite_div')
        container = self.wait_until('content')
        elements = container.find_elements_by_class_name('row-product')
        retries = 0
        while retries < 5 and not elements:
            retries += 1
            elements = container.find_elements_by_class_name('row-product')
        yield tuple(elements)
    
    def __is_element_exist(self, el: str):
        try:
            # self.client.find_element_by_id(el)
            decline_btn = self.client.find_element_by_id('mcx_decline')
            decline_btn.click()
            return True
        except:
            return False

    def __download_pdf(self, url: str):
        main_client = self.client.current_window_handle
        self.client.execute_script("window.open('');")
        self.client.switch_to_window(self.client.window_handles[-1])
        self.client.get(url)
        if self.__is_element_exist('mcx_invite_div'):
            decline_btn = self.client.find_element_by_id('mcx_decline')
            decline_btn.click()            
        efl_element = self.client.find_element_by_xpath(
            '//div[@class="details-contract-documents'+\
                ' details-contract-documents-bottom"]/a[1]')
        self.client.execute_script("arguments[0].click();", efl_element)
        self.client.close()
        self.client.switch_to.window(main_client)
        self.wait_for()
        return self.client
        
    def analyze_element(self, el: WebElement):
        self.__is_element_exist('mcx_invite_div')
        plan_element = el.find_element_by_xpath(
            './/div[@class="positioner"]/h5')
        match = re.search(r'\b\d+\b', plan_element.text)
        if match:
            term = match.group()
        else:
            term = 1
        product_name = plan_element.text
        price_element = el.find_element_by_xpath(
            './/div[@class="left-column"]//div[1]')
        price = re.search(r'(\d+(\.\d+)?)', price_element.text).group()

        detail_element = el.find_element_by_xpath(
            './/div[@class="left-column"]/a[@class="readmore small"]')
        detail_url = detail_element.get_attribute('href')
        self.__download_pdf(detail_url)

        return {
            'term': term,
            'price': price,
            'product_name': product_name,
        }

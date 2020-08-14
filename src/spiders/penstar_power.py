import re
from typing import Tuple, Generator
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from ..libs.engines import SpiderBase


class PstrPowerSpider(SpiderBase):
    name = 'Penstar Power'
    REP_ID = 'PSTR'
    base_url = 'https://penstarpower.com/'

    def submit_zipcode(self, zipcode: str):
        location_element = self.wait_until('aLinkUpdateLocation')
        location_element.click()
        zipcode_element = self.wait_until('txtZipOnPopup')
        zipcode_element.clear()
        zipcode_element.send_keys(zipcode)
        submit_btn = self.wait_until('btnSubmitOnPopup')
        submit_btn.click()

    def get_elements(self) -> Generator[Tuple[WebElement], None, None]:
        container = self.wait_until('//div[@class="marketing"]/div[2]', by=By.XPATH)
        elements = container.find_elements_by_class_name('gridItem')
        retries = 0
        while retries < 5 and not elements:
            retries += 1
            elements = container.find_elements_by_class_name('gridItem')
        yield tuple(elements)
    
    def analyze_element(self, el: WebElement):
        term_element = el.find_element_by_xpath('.//h6//small[2]')
        match = re.search(r'\b\d+\b', term_element.text)
        if match:
            term = match.group()
        else:
            term = 1
        self.wait_for(3)
        price_element = el.find_element_by_xpath('.//div[@class="price-container"]//span')
        price = re.search(r'(\d+(\.\d+)?)', price_element.text).group()

        plan_element = el.find_element_by_xpath('.//div[@class="front"]//h3')
        product_name = plan_element.text

        # Popping up learn more details
        detail_link = el.find_element_by_xpath(
            './/div[@class="front"]//div[@class="txt-center"]/a')
        self.client.execute_script("arguments[0].click();", detail_link)

        modal = self.wait_until(
            '//div[@id="divModelPlanDetails"]/div[@class="modal-dialog"]',
            by=By.XPATH
        )
        efl_element = modal.find_element_by_xpath('.//a[1]')
        self.client.execute_script("arguments[0].click();", efl_element)
        close_btn = modal.find_elements_by_id('lblShowPlnDtlsPopupClose')
        close_btn[0].click()

        return {
            'term': term,
            'price': price,
            'product_name': product_name,
        }

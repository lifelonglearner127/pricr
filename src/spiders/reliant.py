import re
from typing import Tuple, Generator
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from ..libs.engines import SpiderBase


class ReliantSpider(SpiderBase):
    name = 'Reliant'
    REP_ID = 'REL'
    base_url = 'https://www.reliant.com/en/public/reliant-pick-your-free.jsp'

    def submit_zipcode(self, zipcode: str):
        zipcode_element = self.wait_until('zipcode')
        zipcode_element.clear()
        zipcode_element.send_keys(zipcode)
        zipcode_element.send_keys(Keys.ENTER)

    def hook_after_zipcode_submit(self):
        """Click '1000 kWh' toggle
        """
        self.execute_javascript("togglePrice('avgUseOneK')")
        self.wait_for()

    def get_elements(self) -> Generator[Tuple[WebElement], None, None]:
        waiter = self.wait_until(
            '#transTbody .sort-list .sort-item',
            by=By.CSS_SELECTOR)
        elements = self.client.find_elements_by_css_selector(
            '#transTbody .sort-list .sort-item')
        retries = 0
        while retries < 5 and not elements:
            retries += 1
            elements = self.client.find_elements_by_css_selector(
                '#transTbody .sort-list .sort-item')
        yield tuple(elements)
    
    def analyze_element(self, el: WebElement):
        more_detail_button = el.find_element_by_css_selector(
            'a.pcPricingDetails.pcShowPrice.analyticsProductViewDetails')
        more_detail_button.click()

        product_name = el.find_element_by_css_selector(
            'div.pcTopLeftDiv div.planNameDiv span').text

        term = el.find_element_by_css_selector(
            'div.pcTopLeftDiv div.termvalue').get_attribute('data-value')
        
        price = el.find_element_by_css_selector(
            'div.pcTopRightDiv span.avgprice_new span').text

        efl_download_link_element = el.find_element_by_css_selector(
            'div.productDetailsDiv div.planPdfLinks ul li a'
        )
        efl_download_link_element.click()

        return {
            'term': term,
            'price': price,
            'product_name': product_name,
        }

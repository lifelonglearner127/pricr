import re
from typing import Tuple, Generator
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from ..libs.engines import SpiderBase


class ConsEnergySpider(SpiderBase):
    name = 'Constellation Energy'
    REP_ID = 'CONS'
    base_url = 'https://www.constellation.com/'

    def submit_zipcode(self, zipcode: str):
        zipcode_element = self.wait_until('residentialZipCodeText')
        zipcode_element.clear()
        zipcode_element.send_keys(zipcode)
        zipcode_element.send_keys(Keys.ENTER)

    def hook_after_zipcode_submit(self):
        """Click 'SEE ALL PLANS' buttone
        """
        see_all_plans_btn = self.wait_until('signUpFormStepOneSubmit')
        see_all_plans_btn.click()

    def get_elements(self) -> Generator[Tuple[WebElement], None, None]:
        container = self.wait_until('individual-electricity-options')
        elements = container.find_elements_by_css_selector(
            'ul.individual-option-list div.individual-option-main')
        retries = 0
        while retries < 5 and not elements:
            retries += 1
            elements = container.find_elements_by_css_selector(
                'div.individual-option-list div.individual-option-main')
        yield tuple(elements)
    
    def analyze_element(self, el: WebElement):
        term_element = el.find_element_by_css_selector(
            'div.individual-option-main ul.individual-options-short-list span.li-text')
        term = re.search(r'\b\d+\b', term_element.text).group()
        
        price_element = el.find_element_by_css_selector(
            'div.individual-option-main div.individual-cost ')
        price = re.search(r'(\d+(\.\d+)?)', price_element.text).group()

        plan_element = el.find_element_by_css_selector(
            'div.individual-option-main span.name-above-plan')
        product_name = plan_element.text

        efl_download_link_element = el.find_element_by_xpath(
            './/div[@class="individual-plan-doc"]/a[1]'
        )

        main_client = self.client.current_window_handle
        self.client.get(efl_download_link_element.get_attribute('href'))
        self.client.switch_to.window(main_client)

        return {
            'term': term,
            'price': price,
            'product_name': product_name,
        }

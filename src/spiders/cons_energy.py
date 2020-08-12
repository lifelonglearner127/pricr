import re
from typing import Tuple, Generator
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from ..libs.engines import SpiderBase


class ConsEnergySpider(SpiderBase):
    name = 'ConsEnergy'
    REP_ID = 'CONS'
    base_url = 'https://www.constellation.com/'

    def submit_zipcode(self, zipcode: str):
        zipcode_element = self.client.find_element_by_id('residentialZipCodeText')
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
            '//div[@class="individual-docs"]\
                //a[@ng-href="/bin/residential/Terms_TX?versionNum=01YD6"]'
        )
        efl_download_link_element.click()

        return {
            'term': term,
            'price': price,
            'product_name': product_name,
        }

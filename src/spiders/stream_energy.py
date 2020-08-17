import re
from typing import List, Tuple, Generator
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from src.libs.models import Entry
from ..libs.engines import SpiderBase


class StreamEnergySpider(SpiderBase):
    name = 'Stream Energy'
    REP_ID = 'STRM'
    base_url = 'http://www.mystream.com/'

    def run(self, zipcodes: List[str]) -> List[Entry]:
        for zipcode in zipcodes:
            self.log("Visiting %s" % self.base_url)
            self.client.get(self.base_url)
            self.log("Starting with %s..." % zipcode)
            try:
                self.extract(zipcode)
            except:
                continue
        self.log("Finished!")
        return self.data

    def submit_zipcode(self, zipcode: str):
        select_state_btn = self.client.find_element_by_xpath(
            '//button[@class="btn btn-primary dropdown-toggle icon texas"]'
        )
        select_state_btn.click()
        texas_icon = self.wait_until(
            '//a[@class="icon texas"]',
            by=By.XPATH
        )
        texas_icon.click()
        zipcode_element = self.wait_until(
            '//div[@class="location group clearfix"]/input',
            by=By.XPATH)
        zipcode_element.clear()
        zipcode_element.send_keys(zipcode)
        zipcode_element.click()
        self.wait_for(5)
        zipcode_select = self.client.find_element_by_xpath(
            '//ul[@class="typeahead dropdown-menu ng-isolate-scope"]'
        )
        self.wait_for()
        zipcode_select.click()

        if self.__is_element_exist('//div[@ng-if="errorMessage"]'):
            self.log("didn't recognize this %s." % zipcode)
            raise Exception("didn't recognize this {}.".format(zipcode))
        switch_provider_btn = self.client.find_element_by_xpath(
            '//div[@class="radio-options"]/span[1]/input')
        switch_provider_btn.click()

        view_rates_btn = self.client.find_element_by_xpath(
            '//button[@class="view-rates"]'
        )
        view_rates_btn.click()

    def __is_element_exist(self, el: str):
        try:
            self.client.find_element_by_xpath(el)
            return True
        except:
            return False

    def get_elements(self) -> Generator[Tuple[WebElement], None, None]:
        self.wait_for(10)
        container = self.wait_until(
            '//div[@class="enrollment__utility-plans ng-scope"]', by=By.XPATH)
        elements = container.find_elements_by_xpath(
            '//div[@class="hide-large mobile ng-scope"]')
        retries = 0
        while retries < 5 and not elements:
            self.wait_for(2)
            retries += 1
            elements = container.find_elements_by_xpath(
                '//div[@class="hide-large mobile ng-scope"]')
        yield tuple(elements)
    
    def analyze_element(self, el: WebElement):
        # Popping up learn more details
        detail_link = el.find_element_by_xpath('.//tfoot//td//a')
        self.client.execute_script("arguments[0].click();", detail_link)

        modal = self.wait_until(
            '//div[@class="plan-details-modal"]',
            by=By.XPATH
        )
        plan_element = self.client.find_element_by_xpath(
            "//div[@class='plan-details-modal']" +\
                "//div[@class='modal-header']/h2")
        product_name = plan_element.text
        term_element= self.client.find_element_by_xpath(
            "//div[@class='plan-details-modal']//div[@class='modal-body']" +\
                "//div[@class='card'][2]//p[1]")
        match = re.search(r'\b\d+\b', term_element.text)
        if match:
            term = match.group()
        else:
            term = 1
        price_element = self.client.find_element_by_xpath(
            "//div[@class='plan-details-modal']//div[@class='modal-body']" +\
                "//div[@class='card'][1]//p[1]")
        price = re.search(r'(\d+(\.\d+)?)', price_element.text).group()

        efl_element = self.client.find_element_by_xpath(
            "//div[@class='plan-details-modal']//div[@class='modal-footer']" +\
                "//ul//li[1]/a")
        self.client.execute_script("arguments[0].click();", efl_element)
        self.wait_for()
        close_btn = modal.find_element_by_xpath(
            '//div[@class="modal-body"]/div[4]/button')
        self.client.execute_script("arguments[0].click();", close_btn)
        return {
            'term': term,
            'price': price,
            'product_name': product_name,
        }

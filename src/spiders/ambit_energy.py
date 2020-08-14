from typing import Tuple, Generator
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from ..libs.engines import SpiderBase


class AmbitEnergySpider(SpiderBase):
    name = 'Ambit Energy'
    REP_ID = 'AMBT'
    base_url = 'https://ambitenergy.com/rates-and-plans'

    def submit_zipcode(self, zipcode: str):
        form_element = self.wait_until('rates1', timeout=30)
        customer_type_element = form_element.find_element_by_id('residential')
        customer_type_element.click()
        customer_element = form_element.find_element_by_id(
            'no-currentcustomer'
        )
        customer_element.click()
        zipcode_element = form_element.find_element_by_id('zip')
        zipcode_element.send_keys(zipcode)
        zipcode_element.send_keys(Keys.ENTER)

    def hook_after_zipcode_submit(self):
        self.wait_for(30)

    def get_elements(self) -> Generator[Tuple[WebElement], None, None]:
        container = self.wait_until('plan-cards', by=By.CLASS_NAME)
        elements = container.find_elements_by_css_selector(
            'div.stagger-animation.plan-card-container')
        retries = 0
        while retries < 5 and not elements:
            retries += 1
            elements = container.find_elements_by_css_selector(
                'div.stagger-animation.plan-card-container')
        yield tuple(elements)

    def analyze_element(self, el: WebElement):
        # product
        product_name = el.find_element_by_css_selector(
            'h6.tcenter.boldtext.ng-binding'
        ).text

        # download & term
        # open the modal
        detail_element = el.find_element_by_xpath(".//a")
        detail_element.click()
        self.wait_for()

        dialog_element = self.wait_until('ngdialog-content', by=By.CLASS_NAME)

        dd_elements = dialog_element.find_elements_by_xpath('.//dd')
        price_text = dd_elements[0].text
        price = price_text[:price_text.find('.') + 2]

        term = dd_elements[-2].text
        term = term.rstrip('Months')
        try:
            term = int(term)
        except ValueError:
            term = 1

        links = dialog_element.find_elements_by_xpath('.//ul/li')
        links[1].click()

        button_element = dialog_element.find_element_by_xpath('.//input')
        button_element.click()

        return {
            'term': term,
            'price': price,
            'product_name': product_name,
        }

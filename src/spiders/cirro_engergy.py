from typing import Tuple, Generator
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from ..libs.engines import SpiderBase


class CirroEnergySpider(SpiderBase):
    name = 'Cirro Energy'
    REP_ID = 'CIRRO'
    base_url = 'https://www.cirroenergy.com/'

    def submit_zipcode(self, zipcode: str):
        zipcode_element = self.wait_until('txtZipcode', timeout=30)
        zipcode_element.clear()
        zipcode_element.send_keys(zipcode)
        zipcode_element.send_keys(Keys.ENTER)

    def hook_after_zipcode_submit(self):
        self.wait_for(5)

    def get_elements(self) -> Generator[Tuple[WebElement], None, None]:
        container = self.wait_until('paddingbtm', by=By.CLASS_NAME)
        elements = container.find_elements_by_css_selector(
            'div.pricing-table--standard')
        retries = 0
        while retries < 5 and not elements:
            retries += 1
            elements = container.find_elements_by_css_selector(
                'div.pricing-table--standard')
        yield tuple(elements)

    def analyze_element(self, el: WebElement):
        # term
        term_element = el.find_element_by_css_selector(
            'div.pricing-table-value-small.ng-binding'
        )
        term_full_text = term_element.text
        unit_text = term_element.find_element_by_xpath('.//span').text
        term_text_index = len(term_full_text) - len(unit_text)
        term = term_full_text[:term_text_index].rstrip()

        # price
        price_element = el.find_element_by_css_selector(
            'div.pricing-table-value.ng-binding'
        )
        price_full_text = price_element.text
        currency_text = price_element.find_element_by_xpath(
            './/sup').text
        price_text_index = len(price_full_text) - len(currency_text)
        price = price_full_text[:price_text_index].rstrip()

        # product
        product_name = el.find_element_by_css_selector(
            'h1.pricing-table-title'
        ).text

        # download
        # close the survey dialog box if it is open
        decline_button = self.client.find_element_by_id("mcx_decline")
        if decline_button and decline_button.is_displayed():
            decline_button.click()

        # open modal for getting download link
        signup_form = el.find_element_by_id('signupForm')
        modal_link_element = signup_form.find_element_by_xpath('.//a')
        modal_link_element.click()

        dialog_element = self.client.find_element_by_css_selector(
            'div.modal.active'
        )
        link_element = dialog_element.find_elements_by_xpath(
            './/div//div[@class="modal-body"]/'
            'p[@class="modal-link-container"]/a'
        )[-1]
        link_element.click()

        # close the modal
        button = dialog_element.find_element_by_css_selector(
            'a.plan-modal-link-close'
        )
        button.click()

        return {
            'term': term,
            'price': price,
            'product_name': product_name,
        }

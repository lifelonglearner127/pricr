import re
from typing import Tuple, Generator
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from ..libs.engines import SpiderBase


class FourChangeEnergy(SpiderBase):
    name = '4 Change Energy'
    REP_ID = '4CH'
    base_url = 'https://www.4changeenergy.com/'
    plans_promo_blacklist = ['No Contract']

    def submit_zipcode(self, zipcode: str):
        zipcode_element = self.client.find_element_by_xpath(
            '//form[@id="frmId"]//input[@name="AddressDisplayValue"]')
        zipcode_element.clear()
        zipcode_element.send_keys(zipcode)
        zipcode_element.send_keys(Keys.ENTER)

    def hook_after_zipcode_submit(self):
        # NOTE: When you need to do something after zipcode submission
        pass

    def get_elements(self) -> Generator[Tuple[WebElement], None, None]:
        container = self.wait_until('//main[@role="main"]', By.XPATH)
        elements = container.find_elements_by_xpath(
            './/div[not(contains(@style,"display:none"))]' +
            '[contains(@class, "panel-plan")]' + 
            '[contains(@class, "card")]'
        )
        retries = 0
        while retries < 5 and not elements:
            retries += 1
            elements = container.find_elements_by_xpath(
                './/div[not(contains(@style,"display:none"))]' +
                '[contains(@class, "panel-plan")]' + 
                '[contains(@class, "card")]'
            )
        yield tuple([item for item in elements if item.text])

    def analyze_element(self, el: WebElement):
        data_product_promo = el.get_attribute('data-product-promo')
        if not data_product_promo in self.plans_promo_blacklist:
            term_element = el.find_element_by_css_selector(
                'div.card-body div ul')
            term = term_element.text
            match = re.search(r'(\d+)\s+Months', term)
            if match:
                term = match.groups()[0]
            else:
                raise Exception("Term could not match. (%s)" % term)
        else:
            term = '1'

        price_element = el.find_element_by_css_selector(
            'div.card-body div.modal-body h1' +
            ',div.card-body div.product2.cards_div2 h2')
        price = re.search(
            r'(\d+(\.\d+)?)', price_element.text.split('¢')[0]).groups()[0]

        product_name = el.find_element_by_css_selector(
            'div.card-body div.modal-body h2' +
            ',div.card-body div.product2.cards_div2 h4').text

        efl_download_link_element = el.find_element_by_css_selector(
            'div.modal-footer a')
        efl_download_link_element.click()

        efl_view_page = self.wait_until_iframe()
        self.client.switch_to_window(self.client.window_handles[1])

        pdf_url = self.client.find_element_by_tag_name(
            'iframe').get_attribute("src")
        self.client.get(pdf_url)

        self.client.close()
        self.client.switch_to_window(self.client.window_handles[0])
        self.wait_for()

        return {
            'term': term,
            'price': price,
            'product_name': product_name,
        }

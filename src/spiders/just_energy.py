import re
from typing import Tuple, Generator, List
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from ..libs.models import COMMODITY
from ..libs.engines import UtilityByCommoditySpider


class JustEnergySpider(UtilityByCommoditySpider):
    name = 'Just Energy'
    REP_ID = 'JE'
    # base_url = 'https://www.justenergy.com/'
    base_url = 'https://justenergy.com/residential-plans' +\
        '#/enrollment/US/IL/SVC/residential-plans'

    def submit_zipcode(self, zipcode: str):
        zipcode_element = self.wait_until('postalCode')
        # zipcode_element = self.client.find_element_by_xpath(
        #     '//form//input[@id="postalCode"]')
        zipcode_element.clear()
        zipcode_element.send_keys(zipcode)
        zipcode_element.send_keys(Keys.ENTER)

    def hook_after_zipcode_submit(self):
        self.wait_for(10)

    def check_if_multiple_commodities(self) -> bool:
        try:
            element = self.client.find_element_by_css_selector(
                'div.commodity-selector a')
            return element.is_displayed()
        except NoSuchElementException:
            return False

    def get_commodity_link_elements(self) -> List[WebElement]:
        # self.wait_for(2)
        elements = self.client.find_elements_by_css_selector(
            'div.commodity-selector a.electricity,' +
            'div.commodity-selector a.natural-gas'
        )
        return elements

    def get_commodity(self):
        if self.current_commodity_index == 0:
            return COMMODITY.electricity
        else:
            return COMMODITY.natural_gas

    def get_utilities_count(self) -> int:
        return len(self.get_utility_page_link_elements())

    def visit_or_select_utility_page(self, zipcode: str):
        try:
            selector = Select(self.client.find_element_by_id(
                'utilitySelector'))
            selector.select_by_index(self.current_utility_index + 1)

            next_button = self.client.find_element_by_id(
                'utility-selector-next-button')
            next_button.click()
            self.wait_for(2)
        except Exception:
            pass

    def get_utility_page_link_elements(self) -> List[WebElement]:
        try:
            if self.current_utility_index > 0:
                self.wait_for()
                modal_link = self.client.find_element_by_css_selector(
                    'div.div-utilitydisplay a#a-utilitydisplay-ELE,' +
                    'div.div-utilitydisplay a#a-utilitydisplay-GAS')
                if modal_link.is_displayed():
                    modal_link.click()
                    self.wait_for()

            utility_options = self.client.find_elements_by_css_selector(
                'div.type-utility-selector select#utilitySelector option')
            return utility_options[1:]
        except NoSuchElementException:
            return []

    def check_if_multiple_utilities(self) -> bool:
        return bool(self.get_utility_page_link_elements())

    def get_elements(self) -> Generator[Tuple[WebElement], None, None]:
        self.wait_until(
            'div.product-rows div.product-list-item-v2',
            By.CSS_SELECTOR)
        elements = self.client.find_elements_by_css_selector(
            'div.product-rows div.product-list-item-v2')
        retries = 0
        while retries < 5 and not elements:
            retries += 1
            elements = self.client.find_elements_by_css_selector(
                'div.product-rows div.product-list-item-v2')
        yield tuple(elements)

    def analyze_element(self, el: WebElement):
        self.wait_for(2)
        term_element = el.find_element_by_css_selector(
            'p.plan-term-type')
        term = term_element.text
        match = re.search(r'(\d+)\s+Month', term)
        if match:
            term = match.groups()[0]
        else:
            raise Exception("Term could not match. (%s)" % term)

        price_element = el.find_element_by_css_selector(
            'div.column-price div.price span.currency-unit')
        price = price_element.text.split('¢')[0]

        plan_element = el.find_element_by_css_selector(
            'div.column-title > h4')
        product_name = plan_element.text

        try:
            view_detail_button = el.find_element_by_css_selector(
                'button.tx-view-details-btn')  # ,button.btn-link2')
            view_detail_button.click()
        except NoSuchElementException:
            self.log("No need to expan view details. Skipping...")

        try:
            # efl_download_modal_button = el.find_element_by_xpath(
            #     './/a[@class="plan-documents"]' +
            #     '[contains(text(), "Electricity Facts Label")]')
            efl_download_modal_button = el.find_element_by_xpath(
                './/a[@class="plan-documents"]' +
                '[contains(., "Electricity Facts Label")]' +
                '|.//a[@class="plan-documents"]' +
                '[contains(., "Contract Summary")]')
            efl_download_modal_button.click()

            efl_download_btn = self.wait_until(
                "//div[contains(@class, 'modal-dialog')]" +
                "//div[@class='text-center']/a", By.XPATH)
            efl_download_btn.click()
            skip_download = False

            efl_download_modal = self.client.find_element_by_css_selector(
                'div.modal-dialog div.modal-footer button')
            efl_download_modal.click()

        except NoSuchElementException:
            skip_download = True

        self.wait_for()

        try:
            view_detail_button = el.find_element_by_css_selector(
                'button.tx-view-details-btn')
            view_detail_button.click()
        except NoSuchElementException:
            pass
            # view_detail_button = self.client.find_element_by_css_selector(
            #     'div.modal-dialog div.modal-header button.close')
            # view_detail_button.click()
            # self.wait_for()

        return {
            'term': term,
            'price': price,
            'product_name': product_name,
            'skip_download': skip_download,
        }

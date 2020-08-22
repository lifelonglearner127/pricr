import re
import logging
from typing import Tuple, Generator, List
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from ..libs.engines import SpiderBase
from ..libs.models import COMMODITY


class DirectEnergySpider(SpiderBase):
    name = 'Direct Energy'
    REP_ID = 'DE'
    base_url = 'https://www.directenergy.com/'

    def get_commodity(self) -> str:
        if self.current_commodity_index == 0:
            return COMMODITY.electricity
        elif self.current_commodity_index == 1:
            return COMMODITY.natural_gas
        else:
            self.log(
                "commodity_index is greater than 1.",
                level=logging.ERROR)

    def submit_zipcode(self, zipcode: str):
        self.close_feedback_modal()
        zipcode_element = self.client.find_element_by_xpath(
            '//div[@id="left-initial"]//form//input[@name="zipcode"]')
        zipcode_element.clear()
        zipcode_element.send_keys(zipcode)
        zipcode_element.send_keys(Keys.ENTER)

    def get_elements(self) -> Generator[Tuple[WebElement], None, None]:
        container = self.wait_until('eplans')
        elements = container.find_elements_by_css_selector(
            'div.grid-card div.card')
        retries = 0
        while retries < 5 and not elements:
            retries += 1
            elements = container.find_elements_by_css_selector(
                'div.grid-card div.card')
        yield tuple(elements)

    def analyze_element(self, el: WebElement):
        term_element = el.find_element_by_css_selector(
            'div.grid-card-header div.col.grid-month')
        term = term_element.text
        match = re.search(r'(\d+)\s+Month', term)
        if match:
            term = match.groups()[0]
        else:
            raise Exception("Term could not match. (%s)" % term)

        price_element = el.find_element_by_css_selector(
            'div.rate_container span.rate_amount')
        price = price_element.text

        plan_element = el.find_element_by_css_selector(
            'div.card-body.plan-box div.grid-planName')
        product_name = plan_element.text

        result = {
            'term': term,
            'price': price,
            'product_name': product_name,
            'commodity': self.get_commodity(),
        }
        try:
            efl_download_link_element = el.find_element_by_css_selector(
                'div.card-body.plan-box div.gridPlanLinks span.efl_link a, ' +
                'div.card-body.plan-box div.gridPlanLinks ' +
                'span.rate_plan_link a')
            efl_download_link_element.click()
        except NoSuchElementException:
            self.log("Failed to find EFL Link.", level=logging.WARNING)
            result['skip_download'] = True

        return result

    def check_if_multiple_utilities(self) -> bool:
        self.wait_for(2)
        try:
            multiple_utility_modal = self.client.find_element_by_id(
                'popup-window')
            return multiple_utility_modal.is_displayed()
        except NoSuchElementException as e:
            self.log(str(e))
            return False

    def close_feedback_modal(self):
        try:
            # Check if feedback dialog appears or not
            el = self.client.find_element_by_css_selector(
                '#fsrInvite button#fsrFocusFirst')
            el.click()
            self.wait_for(1)
        except NoSuchElementException:
            pass

    def visit_first_or_next_utility_page(self, zipcode: str):
        super().visit_first_or_next_utility_page(zipcode)

        self.wait_for()
        self.close_feedback_modal()

        self.wait_for()
        self.get_utility_page_link_elements()[
            self.current_utility_index].click()
        self.wait_for()

    def get_utility_page_link_elements(self) -> List[WebElement]:
        try:
            elements = self.client.find_elements_by_css_selector(
                'div#myTabContent div.tab-pane.active ' +
                'div.list-group a.list-group-item-action'
            )
            return elements
        except NoSuchElementException as e:
            self.log(str(e))
            return []

    def get_commodity_link_elements(self) -> List[WebElement]:
        try:
            elements = self.client.find_elements_by_css_selector(
                'div.grid-widget div.fauxTab a')
            return elements
        except NoSuchElementException as e:
            self.log(str(e))
            return []

    def check_if_multiple_commodities(self) -> bool:
        return bool(self.get_commodity_link_elements())

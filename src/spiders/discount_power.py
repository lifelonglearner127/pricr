from typing import Tuple, Generator
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from ..libs.engines import SpiderBase


class DiscountPower(SpiderBase):
    name = "Discount Power"
    REP_ID = "DSCT"
    base_url = "https://www.discountpowertx.com/"

    def submit_zipcode(self, zipcode: str):
        zipcode_element = self.wait_until("headerRateZip")
        zipcode_element.clear()
        zipcode_element.send_keys(zipcode)
        zipcode_element.send_keys(Keys.ENTER)

    def get_elements(self) -> Generator[Tuple[WebElement], None, None]:
        container = self.wait_until("content")
        elements = container.find_elements_by_css_selector("div.offerBox")
        retries = 0
        while retries < 5 and not elements:
            self.wait_for(1)
            elements = container.find_elements_by_css_selector("div.offerBox")
            retries += 1
        yield tuple(elements)

    def analyze_element(self, el: WebElement):
        # term
        term = el.find_element_by_css_selector("span.offerSubTitle").text
        try:
            term = int(term)
        except ValueError:
            term = 1

        # price
        price = el.find_element_by_css_selector("div.rate span").text

        # product
        plan_element = el.find_element_by_xpath(
            './/form/div[@class="offerTitle"]/table/tbody/tr/td/h4'
        )
        plan_full_text = plan_element.text
        price_text = el.find_element_by_xpath(
            './/form/div[@class="offerTitle"]/table/tbody/tr/td/h4/span'
        ).text
        plan_offset = len(plan_full_text) - len(price_text)
        product_name = plan_full_text[:plan_offset].rstrip()

        # download
        decline_button = self.client.find_element_by_id("mcx_decline")
        if decline_button and decline_button.is_displayed():
            decline_button.click()

        link_element = el.find_element_by_xpath(
            './/form/div[@class="offerSpecs"]/ul/li/a'
        )
        link_element.click()

        return {
            "term": term,
            "price": price,
            "product_name": product_name,
        }

from typing import Tuple, Generator
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from ..libs.engines import SpiderBase


class AcaciaOrNowBaseSpider(SpiderBase):
    def submit_zipcode(self, zipcode: str):
        zipcode_element = self.wait_until(
            '//input[@class="form-control zip-text"]',
            by=By.XPATH
        )
        zipcode_element.clear()
        zipcode_element.send_keys(zipcode)
        zipcode_element.send_keys(Keys.ENTER)

    def get_elements(self) -> Generator[Tuple[WebElement], None, None]:
        container = self.wait_until('Plan-selection', by=By.CLASS_NAME)
        elements = container.find_elements_by_css_selector('div.plan-box')
        retries = 0
        while retries < 5 and not elements:
            self.wait_for(1)
            elements = container.find_elements_by_css_selector('div.plan-box')
            retries += 1
        yield tuple(elements)

    def analyze_element(self, el: WebElement):
        main_client = self.client.current_window_handle
        # term
        term = el.find_element_by_xpath(
            './/ul[contains(@class, "plancard-attributes")]/li'
        ).text
        term = 0

        # price
        price_element = el.find_element_by_xpath(
            './/span[@class="average-price"]'
        )
        price_full_text = price_element.text
        currency = el.find_element_by_xpath(
            './/span[@class="average-price"]/span'
        ).text
        price_offset = len(price_full_text) - len(currency)
        price = price_full_text[:price_offset].rstrip()

        # product
        plan_element = el.find_element_by_css_selector('div.plan-price')
        product_name = plan_element.text

        # download
        link_element = el.find_element_by_css_selector(
            'div.mt-auto a.edit-btn'
        )
        link_element.click()
        target_modal = link_element.get_attribute("data-target")[1:]
        modal = self.wait_until(target_modal)
        links = modal.find_elements_by_css_selector("ul.bullet-ul")[-1]
        link = links.find_elements_by_xpath(".//li/a")[-1]
        link.click()
        self.wait_for()

        if main_client != self.client.window_handles[-1]:
            self.client.switch_to_window(main_client)

        button_element = modal.find_element_by_xpath(
            './/div/div/div[@class="modal-header"]/button'
        )
        button_element.click()

        return {
            'term': term,
            'price': price,
            'product_name': product_name,
        }


class AcaciaEnergySpider(AcaciaOrNowBaseSpider):
    name = 'Acacia Energy'
    REP_ID = 'ACAC'
    base_url = 'https://www.acaciaenergy.com/'

from typing import Tuple, Generator
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from ..libs.engines import SpiderBase


class InfiniteEnergySpider(SpiderBase):
    name = 'Infinite Energy'
    REP_ID = 'INFE'
    base_url = 'https://www.infiniteenergy.com/'

    def submit_zipcode(self, zipcode: str):
        zipcode_element = self.wait_until('input-5d1e76d4d265d-0')
        zipcode_element.clear()
        zipcode_element.send_keys(zipcode)
        zipcode_element.send_keys(Keys.ENTER)

    def hook_after_zipcode_submit(self):
        self.client.close()
        self.client.switch_to_window(self.client.window_handles[-1])

    def get_elements(self) -> Generator[Tuple[WebElement], None, None]:
        container = self.wait_until(
            '//div[@class="flex-grid"]',
            by=By.XPATH
        )
        elements = container.find_elements_by_css_selector('div.flex-col')
        retries = 0
        while retries < 5 and not elements:
            retries += 1
            elements = container.find_elements_by_css_selector('div.flex-col')
        yield tuple(elements)

    def analyze_element(self, el: WebElement):
        card_body_elements = el.find_elements_by_xpath(
            './/div[contains(@class, "card")]'
            '/div[contains(@class, "card-body")]/div'
        )

        # term
        term_element = card_body_elements[1].find_element_by_xpath(
            ".//div/span"
        )
        term = term_element.text.lstrip("Term:").rstrip("months").strip()

        # price
        price_element = card_body_elements[0].find_element_by_xpath(".//div")
        price = price_element.text.rstrip('¢')

        # product
        product_name = card_body_elements = el.find_element_by_xpath(
            './/div/div/h2'
        ).text

        # download
        # close the survey dialog box if it is open
        footer_element = el.find_element_by_xpath(
            './/div[contains(@class, "card")]'
            '/div[contains(@class, "card-footer")]'
        )
        dropdown_element = footer_element.find_element_by_xpath('.//button')
        self.wait_for()
        dropdown_element.click()

        link = footer_element.find_element_by_xpath(".//div/a")
        retries = 0
        while not link and retries < 5:
            self.wait_for()
            link = footer_element.find_element_by_xpath(".//div/a")
            retries = 0

        if link:
            link.click()

        return {
            'term': term,
            'price': price,
            'product_name': product_name,
        }

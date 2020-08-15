import re
from typing import Tuple, Generator
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from ..libs.engines import SpiderBase


class FirstChoicePowerSpider(SpiderBase):
    name = 'First Choice Power'
    REP_ID = 'FST'
    base_url = 'https://www.firstchoicepower.com/'

    def submit_zipcode(self, zipcode: str):
        zipcode_element = self.wait_until('search')
        zipcode_element.clear()
        zipcode_element.send_keys(zipcode)
        zipcode_element.send_keys(Keys.ENTER)

    def hook_after_zipcode_submit(self):
        self.wait_for(2)
        tabs_element = self.wait_until("tabs", by=By.CLASS_NAME)
        all_plan_element = tabs_element.find_element_by_xpath(
            './/li[contains(@label, "All")]'
        )

        while "active" not in all_plan_element.get_attribute("class"):
            all_plan_element.click()
            self.wait_for()

    def get_elements(self) -> Generator[Tuple[WebElement], None, None]:
        tabs_element = self.wait_until("tabs", by=By.CLASS_NAME)
        all_plan_element = tabs_element.find_element_by_xpath(
            './/li[contains(@label, "All")]'
        )
        tid = all_plan_element.get_attribute("tid")
        container = self.wait_until(f"tab_{tid}")
        elements = container.find_elements_by_css_selector("div.plan-box")
        yield tuple(elements)

    def analyze_element(self, el: WebElement):
        # term
        term_full_text = el.find_element_by_xpath(
            ".//ul[@class='price-bullet']/li"
        ).text

        try:
            term = re.search(r'\b\d+\b', term_full_text).group()
        except Exception:
            term = 1

        # price
        price = el.find_element_by_xpath(
            ".//div[@class='price-container']/h4/span"
        ).text

        # product
        product_name = el.find_element_by_xpath('.//h3').text

        # download
        # close the survey dialog box if it is open
        link = el.find_elements_by_xpath(
            './/div[@class="gridPlanLinks"]/a'
        )[-1]
        link.click()

        return {
            'term': term,
            'price': price,
            'product_name': product_name,
        }

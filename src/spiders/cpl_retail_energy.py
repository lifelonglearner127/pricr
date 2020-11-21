import re
from typing import Tuple, Generator
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from ..libs.engines import SpiderBase


class CplEnergySpider(SpiderBase):
    name = "CPLR Energy"
    REP_ID = "CPL"
    base_url = "https://www.cplretailenergy.com/"

    def submit_zipcode(self, zipcode: str):
        location_element = self.wait_until("change-address-link")
        location_element.click()
        zipcode_element = self.wait_until(
            '//input[@class="zipcode"]', by=By.XPATH)
        zipcode_element.clear()
        zipcode_element.send_keys(zipcode)
        zipcode_element.send_keys(Keys.ENTER)

    def hook_after_zipcode_submit(self):
        """Click button before retrieving the elements
        """
        self.wait_for()
        all_plans_btn = self.wait_until(
            '//div[@id="priceGridContainer"]//ul/li[2]/a', by=By.XPATH
        )
        all_plans_btn.click()

    def get_elements(self) -> Generator[Tuple[WebElement], None, None]:
        container = self.wait_until("viewAllGrid", by=By.ID)
        elements = container.find_elements_by_class_name("plan-box")
        retries = 0
        while retries < 5 and not elements:
            retries += 1
            elements = container.find_elements_by_class_name("plan-box")
        yield tuple(elements[3:])

    def analyze_element(self, el: WebElement):
        term_element = el.find_element_by_xpath(
            './/ul[@class="price-bullet"]/li[2]')
        match = re.search(r"\b\d+\b", term_element.text)
        if match:
            term = match.group()
        else:
            term = 1
        price_element = el.find_element_by_xpath(
            './/div[@class="price-container"]//span'
        )
        price = re.search(r"(\d+(\.\d+)?)", price_element.text).group()

        plan_element = el.find_element_by_xpath(
            './/div[@class="featuredPlanDescription"]//span'
        )
        product_name = plan_element.text

        efl_element = el.find_element_by_xpath(
            './/div[@class="gridPlanLinks"]/a[3]')
        self.client.execute_script("arguments[0].click();", efl_element)
        self.wait_for(2)

        return {
            "term": term,
            "price": price,
            "product_name": product_name,
        }

import re
from typing import Tuple, Generator, Optional
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from ..libs.expected_conditions import element_has_attribute
from ..libs.engines import SpiderBase


class PowerOfTexasSpider(SpiderBase):
    name = "POWER OF TEXAS"
    REP_ID = "POT"
    base_url = "http://www.poweroftexas.com"

    def submit_zipcode(self, zipcode: str):
        zipcode_element = self.wait_until("txtHomeZip")
        zipcode_element.clear()
        zipcode_element.send_keys(zipcode)
        zipcode_element.send_keys(Keys.ENTER)

    def hook_after_zipcode_submit(self):
        self.wait_until_loader()

    def wait_until_loader(self, timeout: int = 15) -> Optional[WebElement]:
        return WebDriverWait(self.client, timeout).until(
            element_has_attribute((By.ID, "preloader"))
        )

    def get_elements(self) -> Generator[Tuple[WebElement], None, None]:
        container = self.wait_until(
            "div.sf_colsIn.plan-columns", By.CSS_SELECTOR)
        elements = container.find_elements_by_css_selector(
            "div.row div.flip-container.card-plan-b"
        )
        retries = 0
        while retries < 5 and not elements:
            retries += 1
            elements = container.find_elements_by_css_selector(
                "div.row div.flip-container.card-plan-b"
            )
        yield tuple(elements)

    def analyze_element(self, el: WebElement):
        term_element = el.find_element_by_css_selector(
            "div.front > div.card div.card-body "
            + "> div:nth-child(1) p.plan-descrption"
        )
        term = term_element.text
        match = re.search(r"(\d+)\s+months", term)
        if match:
            term = match.groups()[0]
        else:
            term = "1"
            # raise Exception("Term could not match. (%s)" % term)

        price_element = el.find_element_by_css_selector(
            "div.front > div.card div.card-header > p.plan-rate"
        )
        price = price_element.text.split("¢")[0]

        plan_element = el.find_element_by_css_selector(
            "div.front > div.card div.card-header > p.plan-area"
        )
        product_name = plan_element.text

        # self.wait_until_loader()
        # detail_anchor_btn = el.find_element_by_class_name(
        #     'details-button'
        # )
        # detail_anchor_btn.click()

        efl_download_link_element = el.find_element_by_css_selector(
            "div.back > div.card div.card-body "
            + "> div.entrust-plan-doc > ul > li:nth-child(1) a"
        )

        self.client.get(efl_download_link_element.get_attribute("href"))

        return {
            "term": term,
            "price": price,
            "product_name": product_name,
        }

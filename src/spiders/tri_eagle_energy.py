import re
from typing import Tuple, Generator
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from ..libs.engines import SpiderBase


class TriEagleEnergySpider(SpiderBase):
    name = 'TriEagle Energy'
    REP_ID = 'TRI'
    base_url = 'http://www.trieagleenergy.com/'

    def submit_zipcode(self, zipcode: str):
        zipcode_element = self.wait_until('ctl00_txtZipCode')
        zipcode_element.clear()
        zipcode_element.send_keys(zipcode)
        zipcode_element.send_keys(Keys.ENTER)

    def hook_after_zipcode_submit(self):
        """Click 'SEE ALL PLANS' buttone
        """
        container = self.wait_until('content')
        see_all_plans_btn = container.find_elements_by_css_selector(
            "input.colorButton")[0]
        see_all_plans_btn.click()

    def get_elements(self) -> Generator[Tuple[WebElement], None, None]:
        container = self.wait_until('RightContent_pnlDisplayRates')
        elements = container.find_elements_by_xpath(
            "//div[contains(translate(@class, 'PB', 'pb'), 'productbox')]")

        retries = 0
        while retries < 5 and not elements:
            retries += 1
            elements = container.find_elements_by_xpath(
                "//div[contains(translate(@class, 'PB', 'pb'), 'productbox')]")
        yield tuple(elements)

    def analyze_element(self, el: WebElement):
        detail_btn = el.find_element_by_css_selector('input.colorButton')
        self.client.execute_script("arguments[0].click();", detail_btn)
        self.wait_for()

        term_element = el.find_element_by_css_selector(
            'div.term')
        term = re.search(r'\b\d+\b', term_element.text).group()

        price_element = el.find_element_by_css_selector(
            'div.productPrice ')
        price = re.search(r'(\d+(\.\d+)?)', price_element.text).group()
        try:
            plan_element = el.find_element_by_css_selector(
                'div.productName ')
        except Exception:
            plan_element = el.find_element_by_css_selector(
                'div.greenProductName ')
        product_name = plan_element.text

        efl_download_link_element = el.find_element_by_xpath(
            './/table[2]//tbody//tr[5]//td//a[1]'
        )
        efl_download_link_element.click()

        main_client = self.client.current_window_handle
        self.client.switch_to_window(self.client.window_handles[-1])
        self.client.execute_script('window.print();')
        self.client.close()
        self.client.switch_to.window(main_client)
        self.wait_for()

        return {
            'term': term,
            'price': price,
            'product_name': product_name,
        }

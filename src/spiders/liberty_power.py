import re
from typing import Tuple, Generator
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from ..libs.engines import SpiderBase


class LibertyPowerSpider(SpiderBase):
    name = 'Liberty Power'
    REP_ID = 'LIB'
    base_url = 'https://www.libertypowercorp.com/'

    def submit_zipcode(self, zipcode: str):
        zipcode_element = self.wait_until('input_75_8_5')
        zipcode_element.send_keys(zipcode)
        zipcode_element.send_keys(Keys.ENTER)

    def hook_after_zipcode_submit(self):
        self.wait_for(30)

    def get_elements(self) -> Generator[Tuple[WebElement], None, None]:
        try:
            container = self.wait_until('panel-body', by=By.CLASS_NAME)
        except Exception:
            raise TimeoutError
        else:
            elements = container.find_elements_by_css_selector(
                'div.lp-container-plan')
            retries = 0
            while retries < 5 and not elements:
                retries += 1
                elements = container.find_elements_by_css_selector(
                    'div.lp-container-plan')
            yield tuple(elements)

    def analyze_element(self, el: WebElement):
        # product
        product_name = el.find_element_by_xpath(
            './/div/span[@class="plan-name"]'
        ).text

        # price
        price_element = el.find_element_by_xpath(
            './/div/div[@class="plan-wrapper"]/span'
        )
        price = re.search(r'(\d+(\.\d+)?)', price_element.text).group()

        # term
        term = re.search(r'(\d+(\.\d+)?)', product_name).group()

        # download
        link = el.find_elements_by_css_selector("a.plan-link")
        self.client.execute_script("arguments[0].click();", link[1])
        self.wait_for()

        dialog_element = self.wait_until("pdf-modal-dialog", by=By.CLASS_NAME)
        pdf_iframe_element = dialog_element.find_element_by_id("pdfframe")
        self.client.switch_to.frame(pdf_iframe_element)
        download_button = self.wait_until("download")
        download_button.click()
        self.client.switch_to.default_content()

        close_button_element = dialog_element.find_element_by_xpath(
            './/button'
        )
        close_button_element.click()

        return {
            'term': term,
            'price': price,
            'product_name': product_name,
        }

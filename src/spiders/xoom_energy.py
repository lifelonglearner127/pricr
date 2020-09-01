import re
from typing import Tuple, Generator
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from ..libs.engines import SpiderBase, OneOffMixin


class XoomEnergySpider(OneOffMixin, SpiderBase):
    name = "Xoom Energy"
    REP_ID = "XOOM"
    base_url = 'https://xoomenergy.com/'

    def submit_zipcode(self, zipcode: str):
        zipcode_element = self.wait_until(
            '//input[@id="cpTopMain_cpMain_txtSearchHome"]',
            by=By.XPATH
        )
        self.wait_for()
        zipcode_element.clear()
        zipcode_element.send_keys(zipcode)
        rates_btn = self.client.find_element_by_xpath(
            '//input[@id="cpTopMain_cpMain_btnSearch"]'
        )
        rates_btn.click()

    def get_elements(self) -> Generator[Tuple[WebElement], None, None]:
        self.wait_for(3)
        container = self.wait_until(
            '//div[@id="cpTopMain_cpMain_upnlMain"]',
            by=By.XPATH
        )
        for i in range(4):
            plan_tabs = container.find_element_by_xpath(
                './/ul[@id="cpTopMain_cpMain_ucProductChart_ulTabCount"]/' +
                'li[{}]'.format(i+1)
            )
            try:
                plan_tabs.click()
                self.wait_for(1)
            except Exception:
                cls_btn = self.client.find_element_by_id(
                    'cpTopMain_ucAlertMessage_btnCloseAlert')
                cls_btn.click()
                plan_tabs.click()
                self.wait_for(1)

            elements = container.find_elements_by_xpath(
                './/div[@class="dashboard-content"]//' +
                'div[contains(@class,"active")]/div/div')
            yield tuple(elements)

    def analyze_element(self, el: WebElement):

        # Popping up learn more details
        detail_link = el.find_element_by_xpath(
            './/a[@class="utility-details-trigger"]/button')
        self.client.execute_script("arguments[0].click();", detail_link)

        price_element = el.find_element_by_xpath(
            './/div[@class="utility-choice-price"]'
        ).text
        price = re.search(r"(\d+(\.\d+)?)", price_element).group()

        product_name = el.find_element_by_xpath(
            './/div[@class="utility-choice-title"]').text

        match = re.search(r"\b\d+\b", product_name)
        if match:
            term = match.group()
        else:
            term = 1
        self.wait_for(2)
        efl_element = el.find_element_by_xpath(
            './/ul[@class="utility-documents"]/li[6]/a'
        )
        efl_url = efl_element.get_attribute('href')
        self.client.get(efl_url)

        return {
            "term": term,
            "price": price,
            "product_name": product_name,
        }

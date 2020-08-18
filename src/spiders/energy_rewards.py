import re
from typing import Tuple, Generator
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from ..libs.engines import SpiderBase


class EnergyRewardsSpider(SpiderBase):
    name = 'Energy Rewards'
    REP_ID = 'EREW'
    base_url = 'https://www.credoenergy.com/'

    def submit_zipcode(self, zipcode: str):
        check_area_btn = self.wait_until(
            '//a[@class="et_pb_button et_pb_button_0 et_pb_bg_layout_light"]',
            by=By.XPATH
        )
        check_area_btn.click()
        self.client.switch_to_window(self.client.window_handles[1])
        main_client = self.client.current_window_handle
        self.client.switch_to_window(self.client.window_handles[0])
        self.client.close()
        self.client.switch_to.window(main_client)
        zipcode_element = self.wait_until(
            '//div[@id="SelectUtilityForm"]/div[2]/div[1]/div/input',
            by=By.XPATH)
        zipcode_element.clear()
        zipcode_element.send_keys(zipcode)

        resident_btn = self.client.find_element_by_id('RadioResidential')
        self.client.execute_script("arguments[0].click();", resident_btn)
        no_area_element = self.client.find_element_by_xpath(
            '//div[@class="row pt-5"]/div[1]/p')
        retries = 0
        self.wait_for()
        while retries < 5 and no_area_element.is_displayed():
            retries += 1
            zipcode_element.clear()
            zipcode_element.send_keys(zipcode)
            no_area_element = self.client.find_element_by_xpath(
                '//div[@class="row pt-5"]/div[1]/p')
            resident_btn = self.client.find_element_by_id('RadioResidential')
            self.client.execute_script("arguments[0].click();", resident_btn)
        check_rates_btn = self.wait_until(
            '//div[@class="row pt-5"]/div[2]/div[5]/div/button',
            by=By.XPATH
        )
        check_rates_btn.click()

    def get_elements(self) -> Generator[Tuple[WebElement], None, None]:
        self.wait_for(3)
        container = self.wait_until(
            '//div[@class="enroll-form"]', by=By.XPATH)
        try:
            elements = container.find_elements_by_class_name(
                'plan-column-style3')
        except Exception:
            retries = 0
            while retries < 5 and not elements:
                self.wait_for(2)
                retries += 1
                elements = container.find_elements_by_class_name(
                    'plan-column-style3')
        yield tuple(elements)

    def analyze_element(self, el: WebElement):
        # Popping up learn more details
        detail_btm = el.find_element_by_xpath('.//a')
        self.client.execute_script("arguments[0].click();", detail_btm)

        modal = self.wait_until(
            '//div[@class="modal-content"]',
            by=By.XPATH
        )
        plan_element = modal.find_element_by_xpath(
            './/h2[@class="custom-header"]')
        product_name = plan_element.text
        term_element = modal.find_element_by_xpath(
            './/div[@class="container-fluid"]/div[4]/div/p'
        )
        match = re.search(r'\b\d+\b', term_element.text)
        if match:
            term = match.group()
        else:
            term = 1
        price_element = modal.find_element_by_xpath(
            './/div[@class="container-fluid"]/div[3]/div/p')
        price = re.search(r'(\d+(\.\d+)?)', price_element.text).group()

        efl_element = modal.find_element_by_xpath(
            './/div[@class="container-fluid"]/div[4]/div[3]/a[3]')
        self.client.execute_script("arguments[0].click();", efl_element)
        cls_btn = modal.find_element_by_xpath(
            './/button[@class="close text-right"]')
        cls_btn.click()

        return {
            'term': term,
            'price': price,
            'product_name': product_name,
        }

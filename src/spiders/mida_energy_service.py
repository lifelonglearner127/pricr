import re
from typing import Tuple, Generator, Optional
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from ..libs.engines import SpiderBase


class MidaEnergySpider(SpiderBase):
    name = 'MIDAMERICAN ENERGY SERVICES'
    REP_ID = 'MIDA'
    base_url = 'http://www.midamericanenergyservices.com/'

    def submit_zipcode(self, zipcode: str):
        residental_submit = self.wait_until(
            '//input[@type="submit"][@value="View Available Offers"]',
            By.XPATH
        )
        residental_submit.click()

        zipcode_element = self.wait_until('ZipCode')
        zipcode_element.clear()
        zipcode_element.send_keys(zipcode)
        zipcode_element.send_keys(Keys.ENTER)

    def hook_after_zipcode_submit(self):
        self.wait_until_loader()

    def wait_until_loader(self, timeout: int = 15) -> Optional[WebElement]:
        return WebDriverWait(self.client, timeout).until(
            EC.invisibility_of_element_located((By.ID, "loading"))
        )

    def get_elements(self) -> Generator[Tuple[WebElement], None, None]:
        container = self.wait_until('select-program')
        elements = container.find_elements_by_css_selector(
            'div.row div.footer-link-group')
        retries = 0
        while retries < 5 and not elements:
            retries += 1
            elements = container.find_elements_by_css_selector(
                'div.row div.footer-link-group')
        yield tuple(elements)

    def analyze_element(self, el: WebElement):
        plan_id = el.find_element_by_id(
            'SelectedPlanId').get_attribute('value')

        price_element = el.find_element_by_id(
            'averageRate-{}'.format(plan_id))
        price = price_element.text

        plan_element = el.find_element_by_xpath(
            './div[@class="row"]/div[1]/div[2]/strong')
        product_name = plan_element.text

        collapse_btn = self.wait_until(
            '//button[@aria-controls="collapse-{}"]'.format(plan_id),
            By.XPATH
        )
        self.client.execute_script("arguments[0].click();", collapse_btn)

        term_element = self.wait_until(
            '//div[@id="collapse-{}"]/div[1]/div[1]/div[3]'.format(plan_id),
            By.XPATH
        )
        term = term_element.text
        match = re.search(r'(\d+)\s+Months', term)
        if match:
            term = match.groups()[0]
        else:
            raise Exception("Term could not match. (%s)" % term)

        efl_download_link_element = self.wait_until(
            '//div[@id="collapse-{}"]/div[2]/div[1]/a'.format(plan_id),
            By.XPATH)
        efl_download_link_element.click()

        return {
            'term': term,
            'price': price,
            'product_name': product_name,
        }

import re
from typing import Tuple, Generator, Optional, List
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ..libs.engines import SpiderBase
from ..libs.models import Entry


class BulbEnergySpider(SpiderBase):
    name = 'Bulb'
    REP_ID = 'BULB'
    base_url = 'https://www.bulb.com/'

    def extract(self, zipcode: str) -> List[Entry]:
        self.log("Searching with zip code - %s" % zipcode)
        self.submit_zipcode(zipcode)
        if self.hook_after_zipcode_submit():
            for elements in self.get_elements():
                for element in elements:
                    entry = self.convert_to_entry(
                        zipcode, self.analyze_element(element))
                    self.log("Downloading for <%s>..." % entry.product_name)
                    if self.wait_until_download_finish():
                        entry.filename = self.rename_downloaded(
                            zipcode, entry.product_name)
                    self.data.append(entry)

    def submit_zipcode(self, zipcode: str):
        zipcode_element = self.wait_until('zipcode')
        zipcode_element.clear()
        zipcode_element.send_keys(zipcode)
        zipcode_element.send_keys(Keys.ENTER)

    def hook_after_zipcode_submit(self):
        try:
            self.wait_until(
                'span#error-message',
                By.CSS_SELECTOR,
                1
            )
        except Exception:
            self.wait_until(
                '//button[@data-testid="joinBulbButtonTop"]',
                By.XPATH
            )
            return True
        return False

    def get_elements(self) -> Generator[Tuple[WebElement], None, None]:
        container = self.wait_until('root')
        elements = container.find_elements_by_css_selector(
            'main > div:nth-child(2) > ' +
            'div:nth-child(2) > div:nth-child(2) > div')
        retries = 0
        while retries < 5 and not elements:
            retries += 1
            elements = container.find_elements_by_css_selector(
                'main > div:nth-child(2) > ' +
                'div:nth-child(2) > div:nth-child(2) > div')
            self.wait_for(0.5)
        yield tuple(elements)

    def analyze_element(self, el: WebElement):
        detail_btn = self.wait_until(
            '//button[@aria-controls="expander-2"]',
            By.XPATH
        )
        detail_btn.click()
        detail_element = el.find_element_by_id('expander-2')
        term_element = detail_element.find_element_by_xpath(
            '//strong[contains(text(), "Term")]/following-sibling::div')
        term = term_element.text
        match = re.search(r'(\d+)\s+Month', term)
        if match:
            term = match.groups()[0]
        elif term == 'Month to month':
            term = '1'
        else:
            raise Exception("Term could not match. (%s)" % term)

        price_element = el.find_element_by_css_selector(
            'div > div:nth-child(1) > h2 > span')
        price = price_element.text.split("¢")[0]

        plan_element = detail_element.find_element_by_xpath(
            '//strong[contains(text(), "Plan name")]/following-sibling::div')
        product_name = plan_element.text

        pdf_url = detail_element.find_element_by_xpath(
            '//strong[contains(text(), "Plan documents")]' +
            '/following-sibling::ul/' +
            'li/a[contains(text(), "Electricity Facts Label")]'
            ).get_attribute('href')
        self.client.get(pdf_url)

        return {
            'term': term,
            'price': price,
            'product_name': product_name,
        }

    def wait_until_visible(
        self, identifier: str, by: str = By.ID, timeout: int = 15
    ) -> Optional[WebElement]:
        return WebDriverWait(self.client, timeout).until(
            EC.visibility_of_element_located((by, identifier))
        )

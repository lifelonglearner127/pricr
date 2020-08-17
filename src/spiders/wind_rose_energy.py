import re
from typing import Tuple, Generator, Optional, List
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ..libs.engines import SpiderBase
from ..libs.models import Entry


class WindRoseEnergySpider(SpiderBase):
    name = 'WINDROSE ENERGY'
    REP_ID = 'WIND'
    base_url = 'https://www.windroseenergy.com/'
    INVISIBLE_STYLE = 'display: none;'

    def extract(self, zipcode: str) -> List[Entry]:
        self.log("Searching with zip code - %s" % zipcode)
        self.submit_zipcode(zipcode)
        self.hook_after_zipcode_submit()

        pager_nav_element = self.client.find_element_by_css_selector(
            'div.k-pager-wrap.k-grid-pager'
        )
        pager_selectors = pager_nav_element.find_elements_by_css_selector(
            'ul.k-pager-numbers li:not(.k-current-page)'
        )
        for ind, elem in enumerate(pager_selectors):
            if not ind == 0:
                elem.click()
                self.wait_until_invisible('divLoader')

            for elements in self.get_elements():
                for element in elements:
                    entry = self.convert_to_entry(
                        zipcode,
                        self.analyze_element(element)
                    )
                    self.log("Downloading for <%s>..." % entry.product_name)
                    if self.wait_until_download_finish():
                        entry.filename = self.rename_downloaded(
                            zipcode, entry.product_name
                        )
                    self.data.append(entry)

    def submit_zipcode(self, zipcode: str):
        zipcode_element = self.wait_until('Zipcode2')
        zipcode_element.clear()
        zipcode_element.send_keys(zipcode)

        submit_btn = self.wait_until('viewratesbtn2')
        submit_btn.click()

        self.wait_until_invisible('divLoader')
        moreplan = self.wait_until('moreplan', By.CLASS_NAME)
        moreplan.click()

        self.wait_until_invisible('divLoader')
        self.wait_until('PType_4').click()

    def hook_after_zipcode_submit(self):
        self.wait_until_invisible('divLoader')

    def get_elements(self) -> Generator[Tuple[WebElement], None, None]:
        container = self.wait_until(
            'div#DivProducts div.k-grid-content ' +
            'table tbody',
            By.CSS_SELECTOR
            )
        elements = container.find_elements_by_css_selector(
            'div.planbox.miniplanbox')
        retries = 0
        while retries < 5 and not elements:
            retries += 1
            elements = container.find_elements_by_css_selector(
                'div.planbox.miniplanbox')
        yield tuple(elements)

    def analyze_element(self, el: WebElement):
        term_element = el.find_element_by_css_selector(
            'p.planduration')
        term = term_element.text
        match = re.search(r'(\d+)\s+month\(s\)', term)
        if match:
            term = match.groups()[0]
        else:
            raise Exception("Term could not match. (%s)" % term)

        price_element = el.find_element_by_css_selector(
            'p.planprice')
        price = price_element.text.split('¢')[0]

        plan_element = el.find_element_by_css_selector(
            'p.planname')
        product_name = plan_element.text

        efl_download_link_element = el.find_element_by_css_selector(
            'div.planfiles a:nth-child(1)')
        self.client.get(
            efl_download_link_element.get_attribute('href'))

        return {
            'term': term,
            'price': price,
            'product_name': product_name,
        }

    def wait_until_invisible(
        self,
        identifier: str,
        by: str = By.ID,
        timeout: int = 15
    ) -> Optional[WebElement]:
        return WebDriverWait(
            self.client, timeout).until(
                EC.invisibility_of_element_located((by, identifier)))

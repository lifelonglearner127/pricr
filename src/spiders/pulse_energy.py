import os
import re
from typing import Tuple, Generator, List
from shutil import move
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from ..libs.engines import SpiderBase
from src.libs.models import Entry


class PulseEnergySpider(SpiderBase):
    name = 'Pulse Energy'
    REP_ID = 'PLSE'
    base_url = 'https://www.pulsepowertexas.com/' + \
        'enrollment?zipCode=empty&promoCode=empty'

    def submit_zipcode(self, zipcode: str):
        zipcode_element = self.client.find_element_by_xpath('//span/input[1]')
        zipcode_element.clear()
        zipcode_element.send_keys(zipcode)
        zipcode_element.send_keys(Keys.ENTER)

    def get_elements(self) -> Generator[Tuple[WebElement], None, None]:
        container = self.wait_until(
            'plan-blocks', by=By.CLASS_NAME)
        elements = container.find_elements_by_class_name('plan-block')
        retries = 0
        while retries < 5 and not elements:
            retries += 1
            elements = container.find_elements_by_class_name('plan-block')
        yield tuple(elements)
    
    def extract(self, zipcode: str) -> List[Entry]:
        self.log("Searching with zip code - %s" % zipcode)
        self.submit_zipcode(zipcode)
        self.hook_after_zipcode_submit()
        for elements in self.get_elements():
            for element in elements:
                entry = self.convert_to_entry(
                    zipcode,
                    self.analyze_element(element)
                )
                self.log("Downloading for <%s>..." % entry.product_name)
                if self.wait_until_download_finish():
                    entry.filename = self.rename_downloaded(
                        zipcode, entry.product_name, entry.price
                    )
                self.data.append(entry)

    def __download_html_to_pdf(self, el: WebElement):
        el.click()

        main_client = self.client.current_window_handle
        self.client.switch_to_window(self.client.window_handles[-1])
        self.client.execute_script('window.print();')
        self.wait_for()
        self.client.close()
        self.client.switch_to.window(main_client)
        return self.client
    
    def rename_downloaded(self, zipcode: str, product_name: str, price: str) -> str:
        filename = self._get_last_downloaded_file()
        product_name = re.sub(r'[^a-zA-Z0-9]+', '', product_name)
        new_filename = f'TODD-{self.REP_ID}-{zipcode}-{product_name}-{price}.pdf'
        move(
            filename,
            os.path.join(self.client.get_pdf_download_path(), new_filename)
        )
        self.wait_for()
        return new_filename

    def analyze_element(self, el: WebElement):
        product_element = el.find_element_by_xpath('.//div[@class="padding"]//h4')
        product_name = product_element.text
        match = re.search(r'(\d+)\s+Month', product_name)
        if match:
            term = match.groups()[0]
        else:
            term = 1

        price_element = el.find_element_by_xpath(
            './/div[@class="padding"]//div[2]')
        price = re.search(r'(\d+(\.\d+)?)', price_element.text).group()

        efl_download_link_element = el.find_element_by_xpath(
            './/div[@class="padding"]/div[2]//a[1]')
        print(efl_download_link_element.get_attribute('href'))
        self.__download_html_to_pdf(efl_download_link_element)

        return {
            'term': term,
            'price': price,
            'product_name': product_name,
        }

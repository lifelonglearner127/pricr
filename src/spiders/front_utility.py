import re
from typing import Tuple, Generator, List
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from src.libs.models import Entry
from .gexa_energy import GexaEnergySpider


class FrontUtilSpider(GexaEnergySpider):
    name = 'Frontier Utilities'
    REP_ID = 'FRT'
    base_url = 'https://newenroll.frontierutilities.com/Home/Index?Zip={zip}'

    def run(self, zipcodes: List[str]) -> List[Entry]:
        for zipcode in zipcodes:
            url = self.base_url.format(zip=zipcode)
            self.log("Visiting %s" % url)
            self.client.get(url)
            self.log("Starting for %s..." % zipcode)
            self.extract(zipcode)
        self.log("Finished!")
        return self.data

    def hook_after_zipcode_submit(self):
        """Switch to show all the plans
        """
        show_all_link = self.wait_until(
            '//div[@id="tabs"]/ul/li[6]/a',
            by=By.XPATH
        )
        show_all_link.click()
        self.wait_until_document_ready()

        option_1k_link = self.wait_until(
            '//span[@class="kwh_choice_container"]//label[@for="1000kwh"]',
            by=By.XPATH
        )
        option_1k_link.click()
        self.wait_until_document_ready()
        self.wait_for(3)
    
    def extract(self, zipcode: str) -> List[Entry]:
        self.log("Searching with zip code - %s" % zipcode)
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
                        zipcode, entry.product_name
                    )
                self.data.append(entry)

    # def analyze_element(self, el: WebElement):
    #     self.wait_until(
    #         'div#divInfo div.container div.row.text-center ' +
    #         'div.plan_price_element span.plan_price_value',
    #         by=By.CSS_SELECTOR
    #     )
    #     self.wait_until_document_ready()
            
    #     price_element = el.find_element_by_css_selector(
    #         'div.plan_price_element span.plan_price_value')
    #     price = price_element.text

    #     # Popping up learn more details
    #     learn_more_link = el.find_element_by_css_selector(
    #         'span.learn_more_item_text')
    #     learn_more_link.click()

    #     modal = self.wait_until('ProductDetailInfo')
    #     product_name = self.wait_until('div#ProductDetailInfo h3', by=By.CSS_SELECTOR).text

    #     term_element = modal.find_elements_by_css_selector('ul li.mb-2')[0]
    #     raw_text = term_element.text
    #     term = re.search(r'Term\s+:\s+(\d+)\s+months', raw_text).groups()[0]

    #     efl_download_link_element = modal.find_elements_by_css_selector(
    #         'a.learn_more_item_text')[0]
    #     efl_download_link_element.click()
    #     close_button = self.wait_until(
    #         'div#ProductDetails div.modal-content button.close',
    #         by=By.CSS_SELECTOR
    #     )
    #     close_button.click()
    #     self.wait_until_document_ready()

    #     return {
    #         'term': term,
    #         'price': price,
    #         'product_name': product_name,
    #     }

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

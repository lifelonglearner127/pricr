import re
from typing import Tuple, Generator, List
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from src.libs.models import Entry
from ..libs.engines import SpiderBase


class TitanGasPowerSpider(SpiderBase):
    name = "Titan Gas and Power"
    REP_ID = "TITAN"
    base_url = (
        "https://rates.cleanskyenergy.com:8443/rates/index?zipcode={zip}"
    )

    def run(self, zipcodes: List[str]) -> List[Entry]:
        for zipcode in zipcodes:
            url = self.base_url.format(zip=zipcode)
            self.log("Visiting %s" % url)
            self.client.get(url)
            self.log("Starting for %s..." % zipcode)
            self.extract(zipcode)
        self.log("Finished!")
        return self.data

    def extract(self, zipcode: str) -> List[Entry]:
        self.log("Searching with zip code - %s" % zipcode)
        for elements in self.get_elements():
            for element in elements:
                entry = self.convert_to_entry(
                    zipcode, self.analyze_element(element))
                self.log("Downloading for <%s>..." % entry.product_name)
                if self.wait_until_download_finish():
                    entry.filename = self.rename_downloaded(
                        zipcode, entry.product_name)
                self.data.append(entry)

    def get_elements(self) -> Generator[Tuple[WebElement], None, None]:
        self.wait_for(3)
        container = self.wait_until(
            '//div[@id="divElectricPlansContainer"]',
            by=By.XPATH
        )
        elements = container.find_elements_by_xpath(
            '//div[@id="divElectricPlans"]/div')
        yield tuple(elements)

    def analyze_element(self, el: WebElement):

        # Popping up learn more details
        detail_link = el.find_element_by_xpath(
            './/div[@id="divPlanButtons"]/div/a')
        self.client.execute_script("arguments[0].click();", detail_link)

        price_element = el.find_element_by_xpath(
            './/div[@id="divPlanRates"]/div/div/span'
        ).text
        price = re.search(r"(\d+(\.\d+)?)", price_element).group()

        product_name = el.find_element_by_xpath(
            './/div[@id="divPlanInformation"]/span').text

        term = re.search(r"\b\d+\b", product_name).group()
        self.wait_for(2)
        efl_element = el.find_element_by_xpath(
            './/div[@class="planContractDoc"]/div/div[2]/a'
        )
        self.client.execute_script("arguments[0].click();", efl_element)
        close_btn = el.find_element_by_xpath(
            '//span[@id="btnExpandPlan"]')
        self.client.execute_script("arguments[0].click();", close_btn)

        return {
            "term": term,
            "price": price,
            "product_name": product_name,
        }

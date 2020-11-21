import re
from typing import Tuple, Generator, List
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from src.libs.models import Entry
from ..libs.engines import SpiderBase


class ChmpEnergySpider(SpiderBase):
    name = "Chmp Energy"
    REP_ID = "CHMP"
    base_url = (
        "https://www.championenergyservices.com/Residential/"
        + "Sign-Up/?promo=&zip={zip}"
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

    def __modal_close(self):
        close_btn = self.wait_until(
            '//button[@class="swal2-close"]', by=By.XPATH)
        close_btn.click()

    def hook_after_zipcode_submit(self):
        """Switch to show all the plans
        """
        self.__modal_close()
        input_element = self.client.find_element_by_class_name("input-number")
        input_element.clear()
        input_element.send_keys("1000")
        btn = input_element.find_element_by_xpath(
            '//button[@onclick="UpdatePrices()"]')
        self.client.execute_script("arguments[0].click();", btn)
        self.wait_for()
        self.__modal_close()

    def extract(self, zipcode: str) -> List[Entry]:
        self.log("Searching with zip code - %s" % zipcode)
        self.hook_after_zipcode_submit()
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
        elements = self.client.find_elements_by_class_name("panel-default")
        yield tuple(elements)

    def analyze_element(self, el: WebElement):
        price_element = el.find_element_by_xpath(
            './/div[@class="average-rate"]//span'
        ).text
        price = re.search(r"(\d+(\.\d+)?)", price_element).group()

        product_name = el.find_element_by_xpath(
            './/div[@class="panel-body"]//h4').text

        term = re.search(r"\b\d+\b", product_name).group()

        # Popping up learn more details
        detail_link = el.find_element_by_xpath("//article//input")
        self.client.execute_script("arguments[0].click();", detail_link)

        modal = self.wait_until('.//div[@id="dnn_ContentPane"]', by=By.XPATH)
        detail_btn = modal.find_element_by_xpath(".//li[2]/a")
        self.client.execute_script("arguments[0].click();", detail_btn)
        efl_element = modal.find_element_by_xpath(
            '//div[@id="dnn_ContentPane"]//fieldset[4]//span//div[2]/a'
        )
        self.client.execute_script("arguments[0].click();", efl_element)
        close_btn = modal.find_element_by_xpath(
            '//div[@class="modal-footer"]//button')
        self.client.execute_script("arguments[0].click();", close_btn)

        return {
            "term": term,
            "price": price,
            "product_name": product_name,
        }

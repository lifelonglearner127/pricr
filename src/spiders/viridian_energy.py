import re
from typing import Tuple, Generator, Optional, List
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ..libs.engines import SpiderBase, OneOffMixin
from ..libs.models import Entry, COMMODITY
from ..libs.browsers import Browser
import calendar
import time
import requests


class ViridianEnergySpider(OneOffMixin, SpiderBase):
    name = "Viridian Energy"
    REP_ID = "VIR"
    base_url = "https://enroll.viridian.com/enroll"
    cities: List[str] = []
    utilities: List[str] = []
    city_url = "/GetLocationsByPostalCode"

    def __init__(self, client: Browser):
        super().__init__(client)
        self.cities.clear()

    def get_available_cities(self, zipcode: str) -> List[str]:
        ts = calendar.timegm(time.gmtime())
        params = {"postalCode": zipcode, "_": ts}
        r = requests.get(url=self.base_url + self.city_url, params=params)
        self.cities = [city["City"] for city in r.json()]

    def get_available_utilities(
        self, zipcode: str, city: str, commodity: str = COMMODITY.electricity
    ) -> List[str]:
        self.submit_zipcode(
            zipcode=zipcode,
            city=city,
            commodity=commodity,
            submit=False,
        )

    def extract(
        self, zipcode: str, commodity: str = COMMODITY.electricity
    ) -> List[Entry]:
        self.log("Searching with zip code - %s" % zipcode)
        self.current_commodity = commodity
        self.get_available_cities(zipcode)

        for city in self.cities:
            self.get_available_utilities(zipcode, city, commodity)
            for utility in self.utilities:
                self.submit_zipcode(
                    zipcode=zipcode,
                    city=city,
                    commodity=commodity,
                    utility=utility,
                )

                for elements in self.get_elements(commodity=commodity):
                    for element in elements:
                        entry = self.convert_to_entry(
                            zipcode, self.analyze_element(element)
                        )
                        self.log(
                            "Skipped downloading <%s>..." % entry.product_name)
                        # if self.wait_until_download_finish():
                        #     entry.filename = self.rename_downloaded(
                        #         zipcode, entry.product_name
                        #     )
                        self.data.append(entry)
                self.client.get(self.base_url)

    def submit_zipcode(
        self,
        zipcode: str,
        city: str,
        commodity: str,
        utility: str = "",
        submit: bool = True
    ):
        zipcode_element = self.wait_until("PostalCode")
        zipcode_element.clear()
        zipcode_element.send_keys(zipcode)

        city_selector = self.wait_until_visible("City")
        city_selector.click()
        city_selector.find_element_by_xpath(
            '//option[contains(text(),"{}")]'.format(city)
        ).click()
        self.wait_until("PropertyTypeResidential").click()
        self.wait_until("PropertyOwnershipOwn").click()

        if commodity == COMMODITY.electricity:
            interest_ele_id = "ElectricUtilityId"
            non_interest_element_id = "NaturalGasUtilityId"
        elif commodity == COMMODITY.natural_gas:
            interest_ele_id = "NaturalGasUtilityId"
            non_interest_element_id = "ElectricUtilityId"

        drop_ele = self.wait_until_visible(non_interest_element_id)
        if not drop_ele.get_attribute("disabled"):
            drp_ele_select = Select(drop_ele)
            drp_ele_select.select_by_value("N/A")

        if submit:
            drop_ele = self.wait_until_visible(interest_ele_id)
            if not drop_ele.get_attribute("disabled"):
                drp_ele_select = Select(drop_ele)
                drp_ele_select.select_by_value(utility)
            self.wait_until("ContinueButton").click()
        else:
            drp_ele = Select(self.wait_until_visible(interest_ele_id))
            self.utilities = [
                element.get_attribute("value")
                for element in drp_ele.options
                if element.get_attribute("value") not in ["", "N/A"]
            ]

    def get_elements(
        self, commodity: str = COMMODITY.electricity
    ) -> Generator[Tuple[WebElement], None, None]:
        if commodity == COMMODITY.electricity:
            container = self.wait_until("ElectricContainer")
        else:
            container = self.wait_until("NaturalGasContainer")

        elements = container.find_elements_by_css_selector(
            "div.ribbon-container"
        )

        retries = 0
        while retries < 5 and not elements:
            retries += 1
            elements = container.find_elements_by_css_selector(
                "div.ribbon-container"
            )
        yield tuple(elements)

    def analyze_element(self, el: WebElement):
        term_element = el.find_element_by_css_selector(
            "div.ribbon-rate-section div.ribbon-rate-wrapper "
            + "div.row:nth-child(2) div.ribbon-label-data"
        )

        term = term_element.text
        match = re.search(r"(\d+)\s+Months", term)
        if match:
            term = match.groups()[0]
        else:
            if term == "Monthly":
                term = "1"
            else:
                raise Exception("Term could not match. (%s)" % term)

        price_element = el.find_element_by_css_selector(
            "div.ribbon-rate-section div.ribbon-rate-wrapper " +
            "div.ribbon-rate"
        )

        price = price_element.text.split("¢")[0]

        plan_element = el.find_element_by_css_selector(
            "div.ribbon-heading-section div.ribbon-heading " + "span"
        )
        product_name = plan_element.text

        # el_class = el.get_attribute("class")
        # el_class_name = re.search(
        #     r"(ribbon-gas-text|ribbon-electric-text)", el_class
        # ).group()
        # if el_class_name == "ribbon-gas-text":
        #     commodity = COMMODITY.natural_gas
        # elif el_class_name == "ribbon-electric-text":
        #     commodity = COMMODITY.electricity
        # else:
        #     commodity = COMMODITY.electricity

        return {
            "term": term,
            "price": price,
            "product_name": product_name,
            "commodity": self.get_commodity(),
        }

    def wait_until_visible(
        self, identifier: str, by: str = By.ID, timeout: int = 15
    ) -> Optional[WebElement]:
        return WebDriverWait(self.client, timeout).until(
            EC.visibility_of_element_located((by, identifier))
        )

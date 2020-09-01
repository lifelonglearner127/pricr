import re
from typing import Tuple, Generator
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from ..libs.engines import SpiderBase, OneOffMixin


class TitanGasPowerSpider(OneOffMixin, SpiderBase):
    name = "Titan Gas and Power"
    REP_ID = "TITAN"
    base_url = \
        "https://rates.cleanskyenergy.com:8443/rates/index?zipcode={zip}"

    def get_base_url(self, zipcode: str) -> str:
        return self.base_url.format(zip=zipcode)

    def submit_zipcode(self, zipcode: str):
        pass

    def get_elements(self) -> Generator[Tuple[WebElement], None, None]:
        self.wait_for(3)
        container = self.wait_until(
            '//div[@id="divElectricPlansContainer"]',
            by=By.XPATH
        )
        elements = container.find_elements_by_xpath(
            '//div[@id="divElectricPlans"]/div')
        yield tuple(elements)

    def __get_efl_link(self, el: WebElement, i: int):
        try:
            el.find_element_by_xpath(
                './/div[@class="planContractDoc"]/div/div[{}]/'.format(i) +
                'a[contains(text(), "Electricity")]')
            return True
        except Exception:
            return False

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
        if self.__get_efl_link(el, 1):
            efl_element = el.find_element_by_xpath(
                    './/div[@class="planContractDoc"]/div/div[1]/a'
                )
        elif self.__get_efl_link(el, 2):
            efl_element = el.find_element_by_xpath(
                './/div[@class="planContractDoc"]/div/div[2]/a'
            )
        else:
            efl_element = el.find_element_by_xpath(
                './/div[@class="planContractDoc"]/div/div[3]/a'
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

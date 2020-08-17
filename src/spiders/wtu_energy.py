from typing import Tuple, Generator
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from .cpl_retail_energy import CplEnergySpider


class WTUEnergySpider(CplEnergySpider):
    name = 'WTU Energy'
    REP_ID = 'WTU'
    base_url = 'https://www.wturetailenergy.com/'

    def get_elements(self) -> Generator[Tuple[WebElement], None, None]:
        container = self.wait_until('viewAllGrid', by=By.ID)
        elements = container.find_elements_by_class_name('plan-box')
        retries = 0
        while retries < 5 and not elements:
            retries += 1
            elements = container.find_elements_by_class_name('plan-box')
        yield tuple(elements[4:])

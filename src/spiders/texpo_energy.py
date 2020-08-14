import time
from typing import Generator, List, Dict
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from ..libs.engines import SpiderBase
from src.libs.models import Entry


class TexpoStyleSpiderBase(SpiderBase):
    def submit_zipcode(self, zipcode: str):
        zipcode_element = self.wait_until("landingPageZipCode")
        zipcode_element.clear()
        zipcode_element.send_keys(zipcode)

        premise_select_element = self.client.find_element_by_xpath(
            '//form[@name="landingPageForm"]//select[@id="premiseType"]'
        )
        premise_select_element.click()
        premise_select_element.find_element_by_xpath(
            '//option[@label="Residential"]'
        ).click()

        submit_btn = self.wait_until('viewRatePlanBtn')
        submit_btn.click()

    def extract(self, zipcode: str) -> List[Entry]:
        self.log("Searching with zip code - %s" % zipcode)
        self.submit_zipcode(zipcode)
        self.hook_after_zipcode_submit()
        for elements in self.get_elements():
            for ind, element in enumerate(elements.get('elements', [])):
                entry = self.convert_to_entry(
                    zipcode,
                    self.analyze_element(
                        element,
                        elements.get('details', [])[ind])
                )
                self.log("Downloading for <%s>..." % entry.product_name)
                if self.wait_until_download_finish():
                    entry.filename = self.rename_downloaded(
                        zipcode,
                        "{}-{}".format(entry.product_name, int(time.time()))
                    )
                self.data.append(entry)

    def get_elements(
        self
    ) -> Generator[Dict[WebElement, WebElement], None, None]:
        # Click all rate plans button
        self.wait_until('allRateplanButton').click()
        container = self.wait_until('ratePlan-container', By.CLASS_NAME)
        elements = container.find_elements_by_css_selector(
            'div.row.name-container')
        details = container.find_elements_by_css_selector(
            'div.row.description-css')
        retries = 0
        while retries < 5 and (not elements or not details):
            retries += 1
            if not elements:
                elements = container.find_elements_by_css_selector(
                    'div.row.name-container')
            elif not details:
                details = container.find_elements_by_css_selector(
                    'div.row.description-css')
        yield {'elements': elements, 'details': details}

    def analyze_element(self, el: WebElement, el_detail: WebElement):
        term_element = el.find_element_by_css_selector(
            'div.term-css div span')
        term = term_element.text

        price_element = el.find_element_by_css_selector(
            'div.type-css div span')
        price = price_element.text.split('¢')[0]

        # Expand detail page
        expand_btn_element = el.find_element_by_css_selector(
            'div.hideButton-css div.buttonCss')
        expand_btn_element.click()

        plan_element = el_detail.find_element_by_css_selector(
            'div:nth-child(1) div h4 b')
        product_name = plan_element.text

        efl_pdf_url = el_detail.find_element_by_css_selector(
            'div.text-center span:nth-child(1) a'
        ).get_attribute("href")
        self.client.get(efl_pdf_url)

        expand_btn_element.click()

        return {
            'term': term,
            'price': price,
            'product_name': product_name,
        }


class TexpoEnergySpider(TexpoStyleSpiderBase):
    name = 'TEXPO Energy'
    REP_ID = 'TEXPO'
    base_url = 'https://enroll.texpoenergy.com/rateplans/'

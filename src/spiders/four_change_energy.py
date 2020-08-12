import re
from typing import Tuple
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from ..libs.engines import SpiderBase


class FourChangeEnergy(SpiderBase):
    name = '4 Change Energy'
    REP_ID = '4CH'
    base_url = 'https://www.4changeenergy.com/'
    plans_section_list = ['most-popular-section', 'plan-grid-section']
    plans_promo_blacklist = ['No Contract']

    def submit_zipcode(self, zipcode: str):
        zipcode_element = self.client.find_element_by_xpath(
            '//form[@id="frmId"]/div[@id="home-rate-finder"]/span[@class="twitter-typeahead"]/input[@name="AddressDisplayValue"]')
        zipcode_element.clear()
        zipcode_element.send_keys(zipcode)
        zipcode_element.send_keys(Keys.ENTER)

    def get_elements(self) -> Tuple[WebElement]:
        
        result = []
        for plan_id in self.plans_section_list:
            container = self.wait_until(plan_id)
            elements = container.find_elements_by_css_selector(
                'div.card.panel-plan')
            retries = 0
            while retries < 5 or not elements:
                retries += 1
                elements = container.find_elements_by_css_selector(
                    'div.card.panel-plan')
            result.extend(elements)
        return tuple(result)

    def analyze_element(self, el: WebElement):
        data_product_promo = el.get_attribute('data-product-promo')
        if not data_product_promo in self.plans_promo_blacklist:
            term_element = el.find_element_by_css_selector(
                'div.card-body div ul')
            term = term_element.text
            match = re.search(r'(\d+)\s+Months', term)
            if match:
                term = match.groups()[0]
            else:
                raise Exception("Term could not match. (%s)" % term)
        else:
            term = '1'
        
        try:
            price_element = el.find_element_by_css_selector(
                'div.card-body div.modal-body h1')
        except:
            price_element = el.find_element_by_css_selector(
                'div.card-body div.product2.cards_div2 h2')
        price = price_element.text.split('¢')[0]

        try:
            plan_element = el.find_element_by_css_selector(
                'div.card-body div.modal-body h2')
        except:
            plan_element = el.find_element_by_css_selector(
                'div.card-body div.product2.cards_div2 h4')
        
        product_name = plan_element.text

        efl_download_link_element = el.find_element_by_xpath(
            '//*[@class="modal-footer justify-content-center"]//a[@data-event-action="Click_efl"]')
        efl_download_link_element.click()

        efl_view_page = self.wait_until_iframe()
        self.client.switch_to_window(self.client.window_handles[1])

        pdf_url = self.client.find_element_by_tag_name('iframe').get_attribute("src")
        self.client.get(pdf_url)

        self.client.close()
        self.client.switch_to_window(self.client.window_handles[0])

        return {
            'term': term,
            'price': price,
            'product_name': product_name,
        }

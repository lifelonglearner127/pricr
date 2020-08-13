import re
from typing import Tuple, Generator, List
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from ..libs.models.entries import Entry
from ..libs.engines import SpiderBase
import time


class TxuEnergy(SpiderBase):
    name = 'TXU Energy'
    REP_ID = 'TXU'
    base_url = 'https://www.txu.com/'
    current_plan = None
    zipcode = None

    def submit_zipcode(self, zipcode: str):
        # Open Plans Modal
        self.zipcode = zipcode
        plans_for_home = self.client.find_element_by_xpath(
            '//section//div[@class="row"]//div[@id="maincontent_1_rptRibbon_rbnBtn_0"]/a'
        )
        plans_for_home.click()

        customer_check_modal = self.wait_until('//div[@id="TrimForAJAX"]//div[@id="main_0_OuterBox"]', By.XPATH)
        new_customer_btn = customer_check_modal.find_element_by_id('newCustJS')
        new_customer_btn.click()

        zipcode_modal = self.wait_until('main_0_pnlProspectCustomer')
        move_to_address = zipcode_modal.find_element_by_css_selector('#main_0_prospectTypeSwitch ~ span')
        move_to_address.click()

        radio_apartment = zipcode_modal.find_element_by_css_selector('#main_0_rdioApartmentNo ~ span')
        radio_apartment.click()

        zipcode_element =zipcode_modal.find_element_by_id('main_0_txtTypeAhead')
        zipcode_element.clear()
        zipcode_element.send_keys(zipcode)

        self.wait_until('//input[@id="main_0_txtTypeAhead"][contains(@class, "match")]', By.XPATH)
        # zipcode_element.send_keys(Keys.ENTER)

        submit_button = zipcode_modal.find_element_by_id('main_0_btnProspect')
        submit_button.click()

    def extract(self, zipcode: str) -> List[Entry]:
        self.log("Searching with zip code - %s" % zipcode)
        self.submit_zipcode(zipcode)
        self.hook_after_zipcode_submit()
        for elements in self.get_elements():
            for element in elements:
                datas = self.analyze_element(element)
                if type(datas) == list:
                    for d in datas:
                        entry = self.convert_to_entry(
                            zipcode,
                            d
                        )
                        self.data.append(entry)
                else:
                    entry = self.convert_to_entry(
                        zipcode,
                        datas
                    )
                    self.log("Downloading for <%s>..." % entry.product_name)
                    if self.wait_until_download_finish():
                        entry.filename = self.rename_downloaded(
                            zipcode, entry.product_name
                        )
                    self.data.append(entry)

    def get_elements(self) -> Generator[Tuple[WebElement], None, None]:
        container = self.wait_until('plans', By.CLASS_NAME)
        elements = container.find_elements_by_css_selector(
            'div.row.ng-scope')
        retries = 0
        while retries < 5 or not elements:
            retries += 1
            elements = container.find_elements_by_css_selector(
                'div.row.ng-scope')
        yield tuple(elements)

    def analyze_element(self, el: WebElement):
        
        # check if see_more_options is exist
        self.current_plan = el
        try:
            plan_entries = []
            show_more_options = el.find_element_by_css_selector('div.btn-detail-plans a#showmoreModal')
            show_more_options.click()
            show_more_modal = self.wait_until('//div[@id="maincontent_0_pnlOfferListing"][@class="miniOfferListing"]', By.XPATH)
            
            more_plans = show_more_modal.find_elements_by_css_selector(
                'div.row')
            retries = 0
            while retries < 5 or not more_plans:
                retries += 1
                more_plans = show_more_modal.find_elements_by_css_selector(
                    'section.plans div.row')
            for p in more_plans:
                entry = self.parse_element(p)
                self.log("Downloading for <%s>..." % entry.get('product_name'))
                if self.wait_until_download_finish():
                    entry['filename'] = self.rename_downloaded(
                        self.zipcode, entry.get('product_name')
                    )
                plan_entries.append(entry)
                time.sleep(2.5)
            show_more_modal.find_element_by_css_selector('a.modal-close').click()
            return plan_entries
        except NoSuchElementException as e:
            # Check if abandPopup is visible
            if not self.check_aband_popup_visible():
                return self.parse_element(el)
            else:
                return self.analyze_element(self.current_plan)
        except Exception as e:
            if not self.check_aband_popup_visible():
                return self.parse_element(el)
            else:
                return self.analyze_element(self.current_plan)

    def parse_element(self, el: WebElement):
        try:
            term_element = el.find_element_by_css_selector(
                'div.term h3 span')
        except:
            term_element = el.find_element_by_css_selector(
                'div.term h2 span')
        term = term_element.text
        match = re.search(r'(\d+)\s+Months', term)
        if match:
            term = match.groups()[0]
        elif term_element.text == 'Month\nto Month':
            term = '1'
        else:
            if not self.check_aband_popup_visible():
                return self.parse_element(el)
            else:
                return self.analyze_element(self.current_plan)
            # raise Exception("Term could not match. (%s)" % term)

        try:
            price_element = el.find_element_by_css_selector(
            'div.rate h3 span')
        except:
            price_element = el.find_element_by_css_selector(
            'div.rate h2 strong')
        
        price = price_element.text.split('¢')[0]

        try:
            plan_element = el.find_element_by_css_selector(
            'h4.plan-title ~ h2')
        except:
            plan_element = el.find_element_by_css_selector(
            'div.plan-details-area h2 span')
            
        product_name = plan_element.text

        # time.sleep(3)
        try:
            collapse_details = el.find_element_by_css_selector('div.plan-details-description a.details')
        except:
            collapse_details = el.find_element_by_css_selector('div.col-sm-12 a.details.confirm-ignore')
        collapse_details.click()
        collapse_id = collapse_details.get_attribute('data-target').split('#')[1]
        print(collapse_id)
        # time.sleep(2)
        efl_download_link_element = el.find_element_by_xpath(
            '//div[@id="{}"]//a[text()="Electricity Facts Label"]'.format(collapse_id))

        pdf_url = efl_download_link_element.get_attribute("href")
        print(pdf_url)
        self.client.get(pdf_url)

        return {
            'term': term,
            'price': price,
            'product_name': product_name,
        }

    def check_aband_popup_visible(self):
        abandPopup = self.client.find_element_by_id('AbandPopup')
        if abandPopup.get_attribute('style') == 'display: block;':
            abandPopup.find_element_by_css_selector('a.closebtn').click()
            time.sleep(5)
            return True
        else:
            return False
        
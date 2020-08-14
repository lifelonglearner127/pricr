import re
from typing import Tuple, Generator
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from ..libs.engines import SpiderBase


class ExprEnergySpider(SpiderBase):
    name = 'Express Energy'
    REP_ID = 'EXPR'
    base_url = 'https://www.myexpressenergy.com/'

    def submit_zipcode(self, zipcode: str):
        zipcode_element = self.client.find_element_by_xpath(
            '//div[@id="home-rate-finder"]//input[@class="typeahead tt-input"]'
        )
        zipcode_element.clear()
        zipcode_element.send_keys(zipcode)
        zipcode_element.send_keys(Keys.ENTER)

    def get_elements(self) -> Generator[Tuple[WebElement], None, None]:
        container = self.wait_until('main-container')
        elements = container.find_elements_by_class_name('panel-plan')
        retries = 0
        while retries < 5 and not elements:
            retries += 1
            elements = container.find_elements_by_css_selector(
                'div.card div.panel-plan')
        yield tuple(elements)

    def __download_pdf(self, url: str):
        main_client = self.client.current_window_handle
        self.client.execute_script("window.open('');")
        self.client.switch_to_window(self.client.window_handles[-1])
        self.client.get(url)
        element = self.client.find_element_by_xpath('//iframe')
        pdf_url = element.get_attribute('src')
        self.client.get(pdf_url)
        self.client.close()
        self.client.switch_to.window(main_client)
        self.wait_for()
        return self.client
    
    def __featured_analyze_element(self, el: WebElement):
        term_element = el.find_element_by_xpath(
            './/ul/li[1]')
        match = re.search(r'\b\d+\b', term_element.text)
        if match:
            term = match.group()
        else:
            term = 1
        
        price_element = el.find_element_by_xpath(
            './/div[@class="row"]//div[2]/div/div/h2')
        price = re.search(r'(\d+(\.\d+)?)', price_element.text).group()

        plan_element = el.find_element_by_xpath(
            './/div[@class="row"]//div[2]/div/div/h4')
        product_name = plan_element.text

        efl_download_link_element = el.find_element_by_xpath(
            './/a[1]')
        efl_url = efl_download_link_element.get_attribute('href')
        self.__download_pdf(efl_url)

        return term, price, product_name
        
    def analyze_element(self, el: WebElement):
        if ('featured-plan' in el.get_attribute('class').split(' ')):
            term, price, product_name = self.__featured_analyze_element(el)
        else:
            term_element = el.find_element_by_xpath(
                './/ul/li[1]')
            match = re.search(r'\b\d+\b', term_element.text)
            if match:
                term = match.group()
            else:
                term = 1
            
            price_element = el.find_element_by_css_selector('div.product2 h2')
            price = re.search(r'(\d+(\.\d+)?)', price_element.text).group()

            plan_element = el.find_element_by_css_selector('div.product2 h4')
            product_name = plan_element.text

            efl_download_link_element = el.find_element_by_xpath('.//a[1]')
            efl_url = efl_download_link_element.get_attribute('href')
            self.__download_pdf(efl_url)

        return {
            'term': term,
            'price': price,
            'product_name': product_name,
        }

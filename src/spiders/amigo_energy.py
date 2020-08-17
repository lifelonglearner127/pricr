import re
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from ..libs.engines import SpiderBase


class AmigoEnergyBaseSpider(SpiderBase):

    def submit_zipcode(self, zipcode: str):
        form_element = self.wait_until('form-get-started')
        zipcode_element = form_element.find_element_by_id('z')
        zipcode_element.send_keys(zipcode)
        zipcode_element.send_keys(Keys.ENTER)

    def hook_after_zipcode_submit(self):
        self.wait_for(2)

    def extract(self, zipcode):
        self.log("Searching with zip code - %s" % zipcode)
        self.submit_zipcode(zipcode)
        self.hook_after_zipcode_submit()

        iframe_element = self.wait_until('iframe', by=By.TAG_NAME)
        self.client.switch_to.frame(iframe_element)

        elements_count = len(
            self.client.find_element_by_xpath(
                '//table[@rules="all"]'
            ).find_elements_by_xpath('.//tr[position()>1]'))
        for i in range(elements_count):
            element = self.client.find_element_by_xpath(
                '//table[@rules="all"]'
            ).find_elements_by_xpath('.//tr[position()>1]')[i]
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

        self.client.switch_to.default_content()

    def analyze_element(self, el: WebElement):
        # product
        product_element = el.find_element_by_xpath('.//td/a')
        product_name = product_element.text

        # term
        term = el.find_element_by_xpath('.//td[3]/span').text

        # price
        price = el.find_element_by_xpath('.//td[2]/span').text
        price = re.search(r'(\d+(\.\d+)?)', price).group()

        # download
        self.client.execute_script("arguments[0].click();", product_element)
        self.wait_for()

        return {
            'term': term,
            'price': price,
            'product_name': product_name,
        }


class AmigoEnergySpider(AmigoEnergyBaseSpider):
    name = 'Amigo Energy'
    REP_ID = 'AMBT'
    base_url = 'https://www.amigoenergy.com/'

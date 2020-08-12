import os
import re
import logging
from time import sleep
from shutil import move
from datetime import datetime
from typing import List, Tuple, Any, Optional, Generator
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.config import Config
from src.libs.browsers import Browser
from src.libs.models import Entry


logging.basicConfig(filename=Config.LOG_FILE, level=logging.INFO)


class SpiderInterface(object):
    name: str = None

    def run(self, zipcodes: List[str]) -> List[Entry]:
        raise NotImplementedError()

    def submit_zipcode(self, zipcode: str) -> None:
        raise NotImplementedError()

    def get_elements(self) -> Generator[Tuple[WebElement], None, None]:
        raise NotImplementedError()

    def analyze_element(self, el: WebElement) -> dict:
        raise NotImplementedError()


class SpiderBase(SpiderInterface):
    REP_ID: str = None
    DOWNLOAD_FILE_PREFIX: str = "TODD"

    name: str = "BASE SPIDER."
    base_url: str = None
    _client: Browser = None
    data: List[Entry] = []

    def __init__(self, client: Browser):
        if not self.base_url:
            raise Exception("base_url is required as a starting point.")

        if not self.REP_ID:
            raise Exception("REP_ID is required to identify.")

        self._client = client
        self.data.clear()

    def log(self, msg: str, level=logging.INFO):
        msg = "{when}:{who} => {what}".format(
            when=datetime.now(),
            who=self.name,
            what=msg)
        logging.log(level, msg)
        print(msg)

    @property
    def client(self) -> Browser:
        return self._client

    def convert_to_entry(self, zipcode: str, data: dict) -> Entry:
        return Entry(
            rep_id=self.REP_ID,
            zipcode=zipcode,
            **data
        )

    def wait_for(self, second: int = 1):
        sleep(second)

    def hook_after_zipcode_submit(self):
        # NOTE: When you need to do something after zipcode submission
        pass

    def extract(self, zipcode: str) -> List[Entry]:
        self.log("Searching with zip code - %s" % zipcode)
        self.submit_zipcode(zipcode)
        self.hook_after_zipcode_submit()
        for elements in self.get_elements():
            for element in elements:
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

    def rename_downloaded(self, zipcode: str, product_name: str) -> str:
        filename = self._get_last_downloaded_file()
        product_name = re.sub(r'[^a-zA-Z0-9]+', '', product_name)
        new_filename = f'TODD-{self.REP_ID}-{zipcode}-{product_name}.pdf'
        move(
            filename,
            os.path.join(self.client.get_pdf_download_path(), new_filename)
        )
        return new_filename

    def _get_last_downloaded_file(self) -> str:
        files = [
            self.client.get_pdf_download_path() + '/' + f
            for f in os.listdir(self.client.get_pdf_download_path())]
        if not files:
            return None
        candiate = max(files, key=os.path.getctime)
        if candiate.startswith(self.DOWNLOAD_FILE_PREFIX):
            return None
        else:
            return candiate

    def run(self, zipcodes: List[str]) -> List[Entry]:
        for zipcode in zipcodes:
            self.log("Visiting %s" % self.base_url)
            self.client.get(self.base_url)
            self.log("Starting with %s..." % zipcode)
            self.extract(zipcode)
        self.log("Finished!")
        return self.data

    def wait_until(
        self,
        identifier: str,
        by: str = By.ID,
        timeout: int = 15
    ) -> Optional[WebElement]:
        element = WebDriverWait(
            self.client, timeout).until(
                EC.presence_of_element_located((by, identifier)))
        return element

    def wait_until_iframe(
        self,
        timeout: int = 15
    ) -> Optional[WebElement]:
        element = WebDriverWait(
            self.client, timeout).until(
                EC.frame_to_be_available_and_switch_to_it(self.client.find_element_by_xpath('//iframe')))
        return element

    def __str__(self):
        return self.name

    def __get_size(self, filename: str) -> int:
        if os.path.isfile(filename): 
            st = os.stat(filename)
            return st.st_size
        else:
            return -1

    def wait_until_download_finish(self) -> bool:
        retries = 0
        MAX_RETRIES = 5
        current_filename = self._get_last_downloaded_file()
        while not current_filename:
            retries += 1
            self.wait_for(retries)
            current_filename = self._get_last_downloaded_file()

        if not current_filename:
            return False
            self.log(
                "Failed to find downloaded file! Skipping...",
                level=logging.ERROR)

        current_size = -1
        retries = 0
        while len(self.client.window_handles) > 1 or\
                current_size != self.__get_size(current_filename):
            retries += 1
            current_size = self.__get_size(current_filename)
            if retries > MAX_RETRIES:
                self.log("Failed to download! Skipping...", level=logging.ERROR)
                return False

            # Keep waiting longer and longer
            self.wait_for(retries)
        # Wait for a second once again
        self.wait_for()
        return True

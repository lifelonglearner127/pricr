import os
import re
import logging
from time import sleep
from shutil import move
from datetime import datetime
from typing import List, Tuple, Optional, Generator
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.config import Config
from src.libs.browsers import Browser
from src.libs.models import Entry, COMMODITY


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

    def extract(self, zipcode: str) -> None:
        raise NotImplementedError()

    def check_if_multiple_utilities(self) -> bool:
        return False

    def check_if_multiple_commodities(self) -> bool:
        return False


class SpiderBase(SpiderInterface):
    REP_ID: str = None
    DOWNLOAD_FILE_PREFIX: str = "TODD"

    name: str = "BASE SPIDER."
    base_url: str = None
    _client: Browser = None
    data: List[Entry] = []

    current_utility_index: int = 0
    current_commodity_index: int = 0
    total_utilities_count: int = 0

    def __init__(self, client: Browser):
        if not self.base_url:
            raise Exception("base_url is required as a starting point.")

        if not self.REP_ID:
            raise Exception("REP_ID is required to identify.")

        self._client = client
        self.data.clear()

    def log(self, msg: str, level=logging.INFO):
        msg = "{when}:{who} => {what}".format(
            when=datetime.now(), who=self.name, what=msg
        )
        logging.log(level, msg)
        print(msg)

    @property
    def client(self) -> Browser:
        return self._client

    def get_commodity(self) -> str:
        return COMMODITY.electricity

    def convert_to_entry(self, zipcode: str, data: dict) -> Entry:
        return Entry(rep_id=self.REP_ID, zipcode=zipcode, **data)

    def wait_for(self, second: int = 1):
        sleep(second)

    def hook_after_zipcode_submit(self):
        # NOTE: When you need to do something after zipcode submission
        pass

    def visit_first_or_next_commodity_page(self, zipcode: str):
        # TODO: Please consider to use self.current_utility_index
        if self.current_commodity_index > 0:
            """When it requires to enter zipcode again
            """
            self.get_commodity_link_elements()[
                self.current_commodity_index].click()
            self.wait_for()

    def iter_all_commodity_pages(self, zipcode: str) -> Generator:
        while self.current_commodity_index < self.get_commodity_link_count():
            self.visit_first_or_next_commodity_page(zipcode)
            yield self.current_commodity_index

    def analyze_single_utility(self, zipcode: str):
        self.log("Analyzing %d-th utility..." % self.current_utility_index)
        self.current_commodity_index = 0

        self.wait_for(1)

        if self.check_if_multiple_commodities():
            for _ in self.iter_all_commodity_pages(zipcode):
                self.log("Parsing %d-th commodity(%s)" % (
                    self.current_commodity_index, self.get_commodity()
                ))
                self.parse_plans_page(zipcode)
                self.current_commodity_index += 1
        else:
            self.parse_plans_page(zipcode)

    def change_location(self, zipcode: str) -> None:
        self.client.get(self.base_url)
        self.submit_zipcode(zipcode)
        self.hook_after_zipcode_submit()

    def change_zipcode(self, zipcode: str) -> None:
        self.change_location(zipcode)

    def visit_or_select_utility_page(self, zipcode: str):
        # TODO: Please consider to use self.current_utility_index
        if self.current_utility_index > 0:
            """When it requires to enter zipcode again
            """
            self.change_zipcode(zipcode)
            self.wait_for()

        # TODO: next utility link should be clicked here.

    def get_utility_page_link_elements(self) -> List[WebElement]:
        return []

    def get_commodity_link_elements(self) -> List[WebElement]:
        return []

    def get_utilities_count(self) -> int:
        return len(self.get_utility_page_link_elements())

    def get_commodity_link_count(self) -> int:
        return len(self.get_commodity_link_elements())

    def iter_all_utilities(self, zipcode: str) -> Generator:
        while self.current_utility_index < self.get_utilities_count():
            self.visit_or_select_utility_page(zipcode)
            self.wait_for()
            yield self.current_utility_index

    def parse_plans_page(self, zipcode: str) -> None:
        self.wait_for(2)
        for elements in self.get_elements():
            for element in elements:
                item = self.analyze_element(element)
                skip_download = item.pop('skip_download', False)
                entry = self.convert_to_entry(
                    zipcode, item)

                if skip_download:
                    self.log(
                        "Skipping download for <%s>" % entry.product_name,
                        level=logging.WARNING
                    )
                else:
                    self.log(
                        "Downloading for <%s>..." % entry.product_name)
                    if self.wait_until_download_finish():
                        entry.filename = self.rename_downloaded(
                            zipcode, entry.product_name)
                self.data.append(entry)

    def extract(self, zipcode: str) -> None:
        """NOTE: Started with submitting a zip code
        When multiple utilies appear, please make sure to submit zipcode.
        """
        self.current_utility_index = 0
        self.current_commodity_index = 0
        self.log("Searching with zip code - %s" % zipcode)
        self.submit_zipcode(zipcode)
        self.hook_after_zipcode_submit()

        if self.check_if_multiple_utilities():
            for _ in self.iter_all_utilities(zipcode):
                self.analyze_single_utility(zipcode)
                self.change_zipcode(zipcode)
                self.wait_for(2)
                self.current_utility_index += 1
        else:
            self.analyze_single_utility(zipcode)

    def __create_filename(self, base_filename: str) -> str:
        path_name = os.path.join(
            self.client.get_pdf_download_path(), base_filename)
        if os.path.isfile(path_name):
            filename, extension = os.path.splitext(base_filename)
            index = 0
            new_filename = f"{filename}-({index}).{extension}"
            path_name = os.path.join(
                self.client.get_pdf_download_path(), new_filename)
            while os.path.isfile(path_name):
                index += 1
                new_filename = f"{filename}-({index}).{extension}"
                path_name = os.path.join(
                    self.client.get_pdf_download_path(),
                    new_filename)
            return new_filename
        else:
            return base_filename

    def rename_downloaded(self, zipcode: str, product_name: str) -> str:
        filename = self._get_last_downloaded_file()
        product_name = re.sub(r"[^a-zA-Z0-9]+", "", product_name)
        new_filename = self.__create_filename(
            f"TODD-{self.REP_ID}-{zipcode}" +
            f"-{self.get_commodity()}-{product_name}.pdf"
        )

        move(filename, os.path.join(
            self.client.get_pdf_download_path(), new_filename))
        self.wait_for()
        return new_filename

    def _get_last_downloaded_file(self) -> str:
        retries = 0
        downloaded_files = self.get_downloaded_files()
        while retries < 3:
            if len(downloaded_files) > 0:
                break
            else:
                downloaded_files = self.get_downloaded_files()
            self.wait_for()
            retries += 1

        if len(downloaded_files) == 0 or not max(
            downloaded_files, key=os.path.getctime
        ):
            return None
        return max(downloaded_files, key=os.path.getctime)

    def get_downloaded_files(self) -> List:
        return [
            self.client.get_pdf_download_path() + "/" + f
            for f in os.listdir(self.client.get_pdf_download_path())
            if not f.startswith(self.DOWNLOAD_FILE_PREFIX)
            and not f.endswith(".crdownload")
        ]

    def run(self, zipcodes: List[str]) -> List[Entry]:
        for zipcode in zipcodes:
            self.log("Visiting %s" % self.base_url)
            self.client.get(self.base_url)
            self.log("Starting with %s..." % zipcode)
            self.extract(zipcode)
        self.log("Finished!")
        return self.data

    def wait_until(
        self, identifier: str, by: str = By.ID, timeout: int = 15
    ) -> Optional[WebElement]:
        return WebDriverWait(self.client, timeout).until(
            EC.element_to_be_clickable((by, identifier))
        )

    def wait_until_iframe(self, timeout: int = 15) -> Optional[WebElement]:
        element = WebDriverWait(self.client, timeout).until(
            EC.frame_to_be_available_and_switch_to_it(
                self.client.find_element_by_xpath("//iframe")
            )
        )
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
            self.wait_for()
            if retries > MAX_RETRIES:
                break
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
                self.log(
                    "Failed to download! Skipping...",
                    level=logging.ERROR)
                return False

            # Keep waiting longer and longer
            self.wait_for(retries)
        # Wait for a second once again
        self.wait_for()
        return True

    def execute_javascript(self, script_command: str):
        return self.client.execute_script(script_command)

    def is_element_clickable(self, identifier: str, by: str = By.ID) -> bool:
        return EC.element_to_be_clickable((by, identifier))


class UtilityByCommoditySpider(SpiderBase):
    def analyze_single_commodity(self, zipcode: str):
        self.log(
            "Analyzing %d-th commodity(%s)..." % (
                self.current_commodity_index,
                self.get_commodity()
            ))
        self.current_utility_index = 0

        self.wait_for()

        if self.check_if_multiple_utilities():
            for _ in self.iter_all_utilities(zipcode):
                self.log(
                    "Analyzing %d-th utility" % self.current_utility_index)
                self.parse_plans_page(zipcode)
                self.current_utility_index += 1
        else:
            self.parse_plans_page(zipcode)

    def extract(self, zipcode: str) -> None:
        """NOTE: Started with submitting a zip code
        When multiple utilies appear, please make sure to submit zipcode.
        """
        self.current_utility_index = 0
        self.current_commodity_index = 0
        self.log("Searching with zip code - %s" % zipcode)
        self.submit_zipcode(zipcode)
        self.hook_after_zipcode_submit()

        if self.check_if_multiple_commodities():
            for _ in self.iter_all_commodity_pages(zipcode):
                self.analyze_single_commodity(zipcode)
                self.current_commodity_index += 1
                self.wait_for(2)
        else:
            self.analyze_single_commodity(zipcode)

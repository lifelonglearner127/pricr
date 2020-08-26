import os
import csv
import time
import logging
from warnings import warn
from typing import List, Dict
from src.config import Config
from src.libs.browsers import Browser
from src.libs.models import Entry
from src.libs.engines import SpiderInterface
from src.spiders import REP_SPIDER_MAPPING


class Crawler(object):
    DOWNLOAD_WAITING_INTERVAL = 1
    __client: Browser = None

    def __init__(self):
        self.__client = Browser()

    @property
    def client(self) -> Browser:
        return self.__client

    def log(self, msg: str, level: int = logging.INFO):
        print(msg)
        logging.log(level, "Crawler: %s" % msg)

    def start(self, todos: Dict[str, List[str]]):
        """Starting point
          - param: todos
            {
                "REP_ID": ["zipcode", "zipcode", ...]
            }
        """
        result = []
        for rep_id, zipcodes in todos.items():
            if rep_id not in REP_SPIDER_MAPPING:
                self.log(
                    "Spider not implemented for %s" % rep_id,
                    level=logging.ERROR)
                continue
            SpiderClass = REP_SPIDER_MAPPING[rep_id]

            try:
                spider = SpiderClass(self.client)
                result += spider.run(zipcodes)
            except Exception as e:
                self.manage_spider_failure(spider, e)

        self.write_to_csv(result)
        self.wait_downloading()

    def write_to_csv(self, entries: List[Entry]):
        report_filename = os.path.join(self.client.report_path, "data.csv")
        headers = [
            "REP_ID",
            "ZipCode",
            "Commodity",
            "Product Name",
            "Price",
            "Term",
            "Filename",
        ]
        if not os.path.isfile(report_filename):
            with open(report_filename, "w+") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
        with open(report_filename, "a") as csvfile:
            writer = csv.writer(csvfile)
            for entry in entries:
                writer.writerow(entry.to_row())

    def __str__(self):
        return self.name

    def manage_spider_failure(self, spider: SpiderInterface, e: Exception):
        # TODO: Here, we should manage spider error case.
        # It can send email or SMS
        if Config.DEBUG:
            raise e
        else:
            self.log(
                "%s failed to scrap data." % spider.name,
                level=logging.ERROR)
            self.log(str(e), level=logging.ERROR)

    def wait_downloading(self):
        # NOTE: Need to wait until downloading is finished.
        retries = 0
        while len(self.client.window_handles) > 1:
            retries += 1
            time.sleep(self.DOWNLOAD_WAITING_INTERVAL)
            if retries > 5:
                warn("Can not wait any more... Skipping.")
                self.client.switch_to_window(self.client.window_handles[-1])
                self.client.close()
                break

        self.client.quit()

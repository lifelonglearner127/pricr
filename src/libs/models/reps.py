import os
import json
from typing import Dict, Optional
from importlib import import_module
from src.config import Config
from src.spiders import SpiderInterface, REP_SPIDER_MAPPING


class RepItem:
    rep_id: str
    name: str
    website: str
    zipcodes: List[str] = []
    crawler: Optional[SpiderInterface] = None

    def __init__(
        self,
        rep_id: str,
        name: str,
        website: str,
        zipcodes: List[str] = [],
        crawler: Optional[str] = None
    ):
        self.rep_id = rep_id.upper()
        self.name = name
        self.website = website
        self.zipcodes = zipcodes
        if rep_id in REP_SPIDER_MAPPING and\
                issubclass(REP_SPIDER_MAPPING[rep_id], SpiderInterface):
            self.crawler = REP_SPIDER_MAPPING[rep_id]

    def __str__(self):
        return f"{self.name}({self.rep_id})"


class RepModel(object):
    __data: Dict[str, RepItem] = {}

    def __init__(self):
        self.__load_data()

    def find_by_id(self, rep_id: str) -> RepItem:
        rep_id = rep_id.upper()
        if rep_id not in self.__data:
            raise Exception("REP with %s not found!" % rep_id)
        else:
            return self.__data[rep_id]

    def __load_data(self):
        db_filename = os.path.join(Config.DB_PATH, 'reps.json')
        with open(db_filename) as content:
            json_content = json.load(content)
            for rep_id, rep_data in json_content.items():
                if rep_id.upper() in self.__data:
                    raise Exception("Duplication found with %s" % rep_id)

                item = RepItem(rep_id, **rep_data)
                self.__data[item.rep_id] = item

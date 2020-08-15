import os
import re
from typing import Tuple, Generator, List
from shutil import move
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from ..libs.engines import SpiderBase
from .pulse_energy import PulseEnergySpider


class NewPowerEnergySpider(PulseEnergySpider):
    name = 'New Power Energy'
    REP_ID = 'NEWP'
    base_url = 'https://newpowertx.com/'

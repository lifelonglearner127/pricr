import os
import re
from typing import Tuple, Generator, List
from shutil import move
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from ..libs.engines import SpiderBase
from .pulse_energy import PulseEnergySpider


class EnergyToGoSpider(PulseEnergySpider):
    name = 'Energy ToGo'
    REP_ID = 'E2GO'
    base_url = 'https://myenergytogo.com/'

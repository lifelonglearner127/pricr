"""
User Defined Selenium Browser
"""
import os
import csv
from datetime import datetime
from sys import platform

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementNotVisibleException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from src.config import Config


class Browser(webdriver.Chrome):
    def __init__(self):
        if platform not in ['win32', 'win64'] and not Config.DEBUG:
            self.display = Display(visible=0, size=(1200, 900))
            self.display.start()

        chromedriver = os.path.join(
            Config.SELENIUM_DRIVER_PATH, self.driver_filename)

        options = webdriver.ChromeOptions()

        options.add_argument("--window-size=1200,900")
        options.add_argument('--dns-prefetch-disable')
        options.add_argument('--js-flags="--max_old_space_size=4096"')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--kiosk-printing')
        prefs = {
            "profile.managed_default_content_settings.images":2,
            "download.default_directory": self.get_pdf_download_path(),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True,
            "savefile.default_directory": self.get_pdf_download_path()
        }
        options.add_experimental_option("prefs",prefs)
    
        super().__init__(chromedriver, chrome_options=options)

    @property
    def driver_filename(self) -> str:
        if platform == 'darwin':
            return 'chromedriver_mac'
        elif platform in ['win32', 'win64']:
            return 'chromedriver.exe'
        else:
            return 'chromedriver_linux'

    @property
    def report_path(self) -> str:
        datetime_str = datetime.now().strftime("%Y-%m-%d")
        return os.path.join(
            Config.DOWNLOAD_BASE_PATH, datetime_str)

    def get_pdf_download_path(self) -> str:
        path = os.path.join(self.report_path, 'PDF')
        if not os.path.isdir(path):
            os.makedirs(path)
        return path

    def quit(self):
        if platform not in ['win32', 'win64'] and not Config.DEBUG:
            self.display.stop()
        super().quit()

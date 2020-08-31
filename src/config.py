import os


class Config:
    DEBUG = bool(os.environ.get('DEBUG'))
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    SELENIUM_DRIVER_PATH = os.path.join(BASE_DIR, 'drivers')
    DOWNLOAD_BASE_PATH = os.path.join(BASE_DIR, 'downloads')
    LOG_FILE = os.path.join(BASE_DIR, 'spider.log')
    DB_PATH = os.path.join(BASE_DIR, 'src', 'mocks')
    USE_YAML = bool(os.environ.get('USE_YAML'), True)

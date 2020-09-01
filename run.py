import os
import sys
import json
import yaml
from src.config import Config
from src.base import Crawler, CrawelrV2


def run_by_yaml(filename: str):
    with open(filename, 'r') as f:
        items = yaml.safe_load(f)

    if items:
        crawler = CrawelrV2()
        crawler.start(items)


def run_by_json(filename: str):
    with open(filename, "r") as content:
        instructions = json.load(content)

    if instructions:
        crawler = Crawler()
        crawler.start(instructions)


def run():
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = 'all'

    if Config.USE_YAML:
        filename += '.yml'
    else:
        filename += '.json'

    filename = os.path.join(Config.BASE_DIR, "src", "mocks", filename)
    if not os.path.isfile(filename):
        raise FileNotFoundError()

    if Config.USE_YAML:
        run_by_yaml(filename)
    else:
        run_by_json(filename)
    print("DONE!")


if __name__ == "__main__":
    run()

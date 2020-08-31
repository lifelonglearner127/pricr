import os
import sys
import json
import yaml
from src.config import Config
from src.base import Crawler, CrawelrV2


def run_by_yaml():
    filename = os.path.join(os.path.dirname(__file__), 'debug.yml')
    if not os.path.isfile(filename):
        return False

    with open(filename, 'r') as f:
        items = yaml.safe_load(f)

    if items:
        crawler = CrawelrV2()
        crawler.start(items)


def run():
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "all.json"
    filename = os.path.join(Config.BASE_DIR, "src", "mocks", filename)
    with open(filename, "r") as content:
        instructions = json.load(content)

    if instructions:
        crawler = Crawler()
        crawler.start(instructions)
    print("DONE!")


if __name__ == "__main__":
    # run()
    run_by_yaml()

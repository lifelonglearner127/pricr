import os
import sys
import json
from argparse import ArgumentParser
from src.config import Config
from src.base import Crawler


def run():
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = 'all.json'
    filename = os.path.join(Config.BASE_DIR, 'src', 'mocks', filename)
    with open(filename, 'r') as content:
        instructions = json.load(content)

    if instructions:
        crawler = Crawler()
        response = crawler.start(instructions)
    print("DONE!")


if __name__ == "__main__":
    run()

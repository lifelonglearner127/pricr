from typing import Tuple
from src.libs.engines import SpiderInterface
from .direct_energy import DirectEnergySpider
from .four_change_energy import FourChangeEnergy


REP_SPIDER_MAPPING = {
    "DE": DirectEnergySpider,
    "4CH": FourChangeEnergy,
}

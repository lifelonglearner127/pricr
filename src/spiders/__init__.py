from typing import Tuple
from src.libs.engines import SpiderInterface
from .direct_energy import DirectEnergySpider
from .four_change_energy import FourChangeEnergy
from .chariot_energy import ChariotEnergySpider
from .txu_energy import TxuEnergy
from .tri_eagle_energy import TriEagleEnergySpider
from .cons_energy import ConsEnergySpider
from .gexa_energy import GexaEnergySpider
from .just_energy import JustEnergySpider


REP_SPIDER_MAPPING = {
    "DE": DirectEnergySpider,
    "4CH": FourChangeEnergy,
    "CHAR": ChariotEnergySpider,
    "TXU": TxuEnergy,
    "TRI": TriEagleEnergySpider,
    "CONS": ConsEnergySpider,
    "GEXA": GexaEnergySpider,
    "JE": JustEnergySpider
}

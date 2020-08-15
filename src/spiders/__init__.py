from typing import Tuple
from src.libs.engines import SpiderInterface
from .direct_energy import DirectEnergySpider
from .four_change_energy import FourChangeEnergy
from .chariot_energy import ChariotEnergySpider
from .txu_energy import TxuEnergy
from .tri_eagle_energy import TriEagleEnergySpider
from .cons_energy import ConsEnergySpider
from .gexa_energy import GexaEnergySpider
from .reliant_energy import ReliantEnergySpider
from .front_utility import FrontUtilSpider
from .just_energy import JustEnergySpider
from .expr_energy import ExprEnergySpider
from .acacia_energy import AcaciaEnergySpider
from .now_power import NowPowerSpider
from .discount_power import DiscountPower
from .cirro_engergy import CirroEnergySpider
from .chmp_energy import ChmpEnergySpider
from .texpo_energy import TexpoEnergySpider
from .yep_energy import YepSpider
from .south_west_pnl import SouthwestPLSpider
from .penstar_power import PstrPowerSpider
from .chmp_energy import ChmpEnergySpider
from .infinite_energy import InfiniteEnergySpider
from .ambit_energy import AmbitEnergySpider
from .spark_energy import SparkEnergySpider
from .cpl_retail_energy import CplEnergySpider
from .think_energy import ThinkEnergySpider
from .grid_plus_energy import GridPlusEnergySpider
from .wtu_energy import WTUEnergySpider
from .first_choice_power import FirstChoicePowerSpider
from .pogo_energy import PogoEnergy


REP_SPIDER_MAPPING = {
    "DE": DirectEnergySpider,
    "4CH": FourChangeEnergy,
    "CHAR": ChariotEnergySpider,
    "TXU": TxuEnergy,
    "TRI": TriEagleEnergySpider,
    "CONS": ConsEnergySpider,
    "GEXA": GexaEnergySpider,
    "REL": ReliantEnergySpider,
    "JE": JustEnergySpider,
    "FRT": FrontUtilSpider,
    "EXPR": ExprEnergySpider,
    "ACAC": AcaciaEnergySpider,
    "NOW": NowPowerSpider,
    "DSCT": DiscountPower,
    "CIRRO": CirroEnergySpider,
    "TEXPO": TexpoEnergySpider,
    "YEP": YepSpider,
    "SWPL": SouthwestPLSpider,
    "PSTR": PstrPowerSpider,
    "CHMP": ChmpEnergySpider,
    "INFE": InfiniteEnergySpider,
    "AMBT": AmbitEnergySpider,
    "SPRK": SparkEnergySpider,
    "CPL": CplEnergySpider,
    "THINK": ThinkEnergySpider,
    "GPLUS": GridPlusEnergySpider,
    "WTU": WTUEnergySpider,
    "GRID": GridPlusEnergySpider,
    "FST": FirstChoicePowerSpider,
    "POGO": PogoEnergy,
}

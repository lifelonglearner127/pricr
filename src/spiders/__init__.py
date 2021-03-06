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
from .infinite_energy import InfiniteEnergySpider
from .ambit_energy import AmbitEnergySpider
from .spark_energy import SparkEnergySpider
from .cpl_retail_energy import CplEnergySpider
from .think_energy import ThinkEnergySpider
from .grid_plus_energy import GridPlusEnergySpider
from .wtu_energy import WTUEnergySpider
from .apge_energy import APGESpider
from .first_choice_power import FirstChoicePowerSpider
from .pogo_energy import PogoEnergy
from .pulse_energy import PulseEnergySpider
from .energy_togo import EnergyToGoSpider
from .lonestar_energy import LSTREnergySpider
from .new_power_spider import NewPowerEnergySpider
from .power_newx import PowerNextSpider
from .v247_energy_spider import V247EnergySpider
from .town_square_energy import TownSquareEnergySpider
from .summer_energy import SummerEnergySpider
from .entrust_energy import EntrustEnergySpider
from .green_mountain_energy import GreenMountEnergySpider
from .viridian_energy import ViridianEnergySpider
from .tomorrow_energy import TomorrowEnergySpider
from .amigo_energy import AmigoEnergySpider
from .tara_energy import TaraEnergySpider
from .liberty_power import LibertyPowerSpider
from .iberdrola import IberdrolaTexasSpider
from .stream_energy import StreamEnergySpider
from .wind_rose_energy import WindRoseEnergySpider
from .bulb_energy import BulbEnergySpider
from .mida_energy_service import MidaEnergySpider
from .power_of_texas import PowerOfTexasSpider
from .energy_rewards import EnergyRewardsSpider
from .xoom_energy import XoomEnergySpider
from .clearview_energy import ClearviewEnergySpider
from .titan_gas_power import TitanGasPowerSpider


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
    "APGE": APGESpider,
    "GRID": GridPlusEnergySpider,
    "FST": FirstChoicePowerSpider,
    "POGO": PogoEnergy,
    "PLSE": PulseEnergySpider,
    "E2GO": EnergyToGoSpider,
    "LSTR": LSTREnergySpider,
    "NEWP": NewPowerEnergySpider,
    "PWRN": PowerNextSpider,
    "V247": V247EnergySpider,
    "TOWN": TownSquareEnergySpider,
    "SUMM": SummerEnergySpider,
    "ENTR": EntrustEnergySpider,
    "GME": GreenMountEnergySpider,
    "VIR": ViridianEnergySpider,
    "TOM": TomorrowEnergySpider,
    "AMIG": AmigoEnergySpider,
    "TARA": TaraEnergySpider,
    "LIB": LibertyPowerSpider,
    "IBER": IberdrolaTexasSpider,
    "STRM": StreamEnergySpider,
    "WIND": WindRoseEnergySpider,
    "BULB": BulbEnergySpider,
    "MIDA": MidaEnergySpider,
    "POT": PowerOfTexasSpider,
    "EREW": EnergyRewardsSpider,
    "XOOM": XoomEnergySpider,
    "CLEAR": ClearviewEnergySpider,
    "TITAN": TitanGasPowerSpider,
}

REP_MULTI_STATE_SPIDER_MAPPING = {
    "DE": DirectEnergySpider,
    "JE": JustEnergySpider,
    "XOOM": XoomEnergySpider,
    "EREW": EnergyRewardsSpider,
    "TITAN": TitanGasPowerSpider,
    "VIR": ViridianEnergySpider,
}

from typing import Tuple
from src.libs.engines import SpiderInterface
from .direct_energy import DirectEnergySpider


def get_available_spiders() -> Tuple[SpiderInterface.__class__]:
    return (
        DirectEnergySpider,
    )


REP_SPIDER_MAPPING = {
    "DE": DirectEnergySpider
}

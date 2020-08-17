from .pulse_energy import PulseEnergySpider


class EnergyToGoSpider(PulseEnergySpider):
    name = "Energy ToGo"
    REP_ID = "E2GO"
    base_url = "https://myenergytogo.com/"

from .pulse_energy import PulseEnergySpider


class PowerNextSpider(PulseEnergySpider):
    name = 'Power Next'
    REP_ID = 'PWRN'
    base_url = 'https://mypowernext.com/'

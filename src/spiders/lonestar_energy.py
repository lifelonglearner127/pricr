from .pulse_energy import PulseEnergySpider


class LSTREnergySpider(PulseEnergySpider):
    name = 'Lonestar Energy'
    REP_ID = 'LSTR'
    base_url = 'https://lonestarenergytx.com/'

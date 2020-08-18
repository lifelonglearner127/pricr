from .pulse_energy import PulseEnergySpider


class NewPowerEnergySpider(PulseEnergySpider):
    name = 'New Power Energy'
    REP_ID = 'NEWP'
    base_url = 'https://newpowertx.com/'

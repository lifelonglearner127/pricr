from .acacia_energy import AcaciaOrNowBaseSpider


class NowPowerSpider(AcaciaOrNowBaseSpider):
    name = 'Now Power'
    REP_ID = 'NOW'
    base_url = 'https://nowpowertexas.com/'

from .texpo_energy import TexpoStyleSpiderBase


class SouthwestPLSpider(TexpoStyleSpiderBase):
    name = 'Southwest Power & Light'
    REP_ID = 'SWPL'
    base_url = 'https://enroll.southwestpl.com/'

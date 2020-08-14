from .texpo_energy import TexpoStyleSpiderBase


class YepSpider(TexpoStyleSpiderBase):
    name = 'YEP Energy'
    REP_ID = 'YEP'
    base_url = 'https://enroll.yepenergy.com/rateplans/'

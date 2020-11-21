from warnings import warn
from .entries import COMMODITY


class Instruction(object):
    _zipcode: str
    _commodity: str = COMMODITY.electricity

    _COMMODITY_MAPPING = {
        'elec': COMMODITY.electricity,
        'gas': COMMODITY.natural_gas
    }

    def __init__(self, zipcode: str, commodity: str = 'elec'):
        self.zipcode = zipcode
        self.commodity = commodity

    @property
    def zipcode(self) -> str:
        return self._zipcode

    @zipcode.setter
    def zipcode(self, value: str):
        self._zipcode = str(value).lower()

    @property
    def commodity(self) -> str:
        return self._commodity

    @commodity.setter
    def commodity(self, value: str):
        value = str(value).lower()
        if value in self.__class__._COMMODITY_MAPPING:
            self._commodity = self.__class__._COMMODITY_MAPPING[value]
        else:
            msg = "Unknown commodity value found - %s" % value
            warn(msg)

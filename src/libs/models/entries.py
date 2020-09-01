import re
from typing import Tuple


class COMMODITY:
    electricity = 'Electricity'
    natural_gas = 'Natural Gas'


class Entry:
    rep_id: str
    zipcode: str
    term: str
    price: float
    product_name: str
    commodity: str = COMMODITY.electricity
    filename: str = ''

    def __init__(
        self,
        rep_id: str,
        zipcode: str,
        term: int,
        price: float,
        product_name: str,
        commodity: str = COMMODITY.electricity,
        filename: str = '',
    ):
        self.rep_id = rep_id.upper()
        self.zipcode = zipcode
        self.term = int(term)
        self.price = float(re.search(r'\d+(\.\d+)?', price).group())
        self.product_name = product_name
        self.filename = filename
        if commodity not in [
            COMMODITY.electricity,
            COMMODITY.natural_gas
        ]:
            self.commodity = COMMODITY.electricity
        else:
            self.commodity = commodity

    def to_row(self) -> Tuple[str]:
        return (
            self.rep_id,
            self.zipcode,
            self.commodity,
            self.product_name,
            "%.2f" % self.price,
            self.term,
            self.filename,
        )

from typing import List
from src.libs.models.instructions import Instruction, COMMODITY


class OneOffMixin:
    current_commodity: str = COMMODITY.electricity

    def get_commodity(self) -> str:
        return self.current_commodity

    def run(self, instructions: List[Instruction]):
        if not all(isinstance(item, Instruction) for item in instructions):
            raise Exception("Argment Error.")

        for inst in instructions:
            self.log("Visiting %s" % self.get_base_url(inst.zipcode))
            self.client.get(self.get_base_url(inst.zipcode))
            self.log(f"Extracting {inst.commodity} for {inst.zipcode}...")
            self.extract(inst.zipcode, inst.commodity)
        self.log("Finished!")
        return self.data

    def extract(
        self, zipcode: str, commodity: str = COMMODITY.electricity
    ) -> None:
        """To make it simple, scrape the first utility for the given
        zip code and commodity
        """
        self.current_commodity = commodity
        self.log("Searching %s with zip code - %s" % (
            commodity, zipcode))
        self.submit_zipcode(zipcode)
        self.hook_after_zipcode_submit()

        if self.check_if_service_unavailable():
            self.log(
                f"Service is not available for {zipcode}"
            )
            return

        if self.check_if_multiple_utilities():
            for _ in self.iter_all_utilities(zipcode):
                self.analyze_single_utility(zipcode, commodity)
                # NOTE: Check the first utility only.
                break
        else:
            self.analyze_single_utility(zipcode, commodity=commodity)

    def analyze_single_utility(
        self, zipcode: str, commodity: str = COMMODITY.electricity
    ):
        if self.check_if_multiple_commodities():
            self.go_to_commodity(commodity)
            self.parse_plans_page(zipcode)
        else:
            if commodity != COMMODITY.electricity:
                self.log(
                    "Please check if you gave the proper commodity option")
            self.parse_plans_page(zipcode)

    def go_to_commodity(self, commodity: str = COMMODITY.electricity):
        """Visit the given commodity page when it shows multiple commodities
        Just after this method, the page should have been ready to be scraped.
        """
        if commodity == COMMODITY.electricity:
            self.get_commodity_link_elements()[0].click()
        elif commodity == COMMODITY.natural_gas:
            self.get_commodity_link_elements()[1].click()
        else:
            self.log("Unexpected commodity found - %s" % commodity)
            return

        self.wait_for()


class UtilityByCommodityMixin:
    ITER_ALL: bool = False

    def analyze_single_commodity(self, zipcode: str):
        if self.ITER_ALL:
            self.log(
                "Analyzing %d-th commodity(%s)..." % (
                    self.current_commodity_index,
                    self.get_commodity()
                ))
            self.current_utility_index = 0

        self.wait_for()

        if self.check_if_multiple_utilities():
            if self.ITER_ALL:
                for _ in self.iter_all_utilities(zipcode):
                    self.log(
                        "Analyzing %d-th utility" % self.current_utility_index)
                    self.parse_plans_page(zipcode)
                    self.current_utility_index += 1
            else:
                self.visit_or_select_utility_page(zipcode)
                self.parse_plans_page(zipcode)
        else:
            self.parse_plans_page(zipcode)

    def extract(
        self, zipcode: str, commodity: str = COMMODITY.electricity
    ) -> None:
        """NOTE: Started with submitting a zip code
        When multiple utilies appear, please make sure to submit zipcode.
        """
        self.log("Searching with zip code - %s" % zipcode)
        self.current_commodity = commodity
        self.submit_zipcode(zipcode)
        self.hook_after_zipcode_submit()

        if self.check_if_service_unavailable():
            self.log(
                f"Service is not available for {zipcode}"
            )
            return

        if self.check_if_multiple_commodities():
            self.go_to_commodity(commodity)
            self.analyze_single_commodity(zipcode)
        else:
            if commodity != COMMODITY.electricity:
                self.log(
                    "Please check if you gave the proper commodity option")
            self.analyze_single_commodity(zipcode)

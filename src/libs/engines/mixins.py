from typing import List
from src.libs.models.instructions import Instruction


class OneOffMixin:
    def run(self, instructions: List[Instruction]):
        if not all(isinstance(item, Instruction) for item in instructions):
            raise Exception("Argment Error.")

        for inst in instructions:
            self.log("Visiting %s" % self.base_url)
            self.client.get(self.base_url)
            self.log(f"Extracting {inst.commodity} for {inst.zipcode}...")
            self.extract(inst.zipcode, inst.commodity)
        self.log("Finished!")
        return self.data

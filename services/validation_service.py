from __future__ import annotations

from models.schema_row import SchemaRow


class ValidationManager:

    def __init__(self):
        self._validators = []

    def register(self, validators):
        self._validators.extend(validators)

    def process(self, row: SchemaRow):
        for v in self._validators:
            v.process(row)

    def finalize(self):
        for v in self._validators:
            v.finalize()

    def generate_results(self):
        return [v.generate_result() for v in self._validators]
    
    def generate_reports(self):  # ✅ compatibility
        return self.generate_results()
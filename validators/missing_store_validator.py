import polars as pl
from models.validation_result import ValidationResult


class MissingStoreValidator:

    def __init__(self):
        self._bau = set()
        self._test = set()
        self._reference = set()
        self._mode = "bau"
        self._mode_type = "existing"

    def set_mode(self, mode):
        self._mode = mode

    def set_reference_stores(self, stores):
        self._reference = set(stores)
        self._mode_type = "onboarding"

    def process(self, row):
        s = row.get("store_id")
        if s:
            if self._mode == "bau":
                self._bau.add(s)
            else:
                self._test.add(s)

    def finalize(self):
        pass

    def generate_result(self):

        # ✅ onboarding
        if self._mode_type == "onboarding":
            missing = self._reference - self._bau

            return ValidationResult(
                validator_name="MissingStoreValidator",
                status="SUCCESS",
                summary={
                    "missing_stores": len(missing),
                },
                report_data=pl.DataFrame({
                    "store": list(missing)
                })
            )

        # ✅ existing
        missing = self._bau - self._test
        additional = self._test - self._bau

        rows = []
        for s in self._bau | self._test:
            if s in missing:
                st = "MISSING"
            elif s in additional:
                st = "NEW"
            else:
                st = "MATCHED"
            rows.append({"store": s, "status": st})

        return ValidationResult(
            validator_name="MissingStoreValidator",
            status="SUCCESS",
            summary={
                "total_stores_bau": len(self._bau),
                "total_stores_test": len(self._test),
                "missing": len(missing),
                "additional": len(additional),
            },
            report_data=pl.DataFrame(rows)
        )
    
    def generate_report(self):
        result = self.generate_result()
        return result.report_data
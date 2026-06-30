from validators.store_validator import StoreValidator
from validators.item_validator import ItemValidator
from validators.missing_store_validator import MissingStoreValidator
from validators.unique_upc_validator import UniqueUPCValidator
from validators.raw_data_review import RawDataReviewValidator
from validators.summary_validator import SummaryValidator


def run_pipeline(file_path, delimiter, date_column, mode):

    # ✅ instantiate
    store_v = StoreValidator()
    item_v = ItemValidator()
    missing_v = MissingStoreValidator()
    upc_v = UniqueUPCValidator()
    raw_v = RawDataReviewValidator(date_column=date_column)

    validators = [store_v, item_v, missing_v, upc_v, raw_v]

    # ✅ set mode
    for v in validators:
        if hasattr(v, "set_mode"):
            v.set_mode(mode)

    # ✅ TODO: replace with real Reader/Parser
    rows = []  # your parsed SchemaRow generator

    for row in rows:
        for v in validators:
            v.process(row)

    for v in validators:
        if hasattr(v, "finalize"):
            v.finalize()

    results = [v.generate_result() for v in validators]

    summary = SummaryValidator()
    summary.consume(results)
    results.append(summary.generate_result())

    return results

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Generator, Iterable

from models import Detail, Payment, Transaction

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class NormalizedRow:
    """
    Represents a flattened row derived from a Transaction.

    Each row combines transaction-level and line-level data.
    """

    transaction_id: int
    record_type: str
    fields: tuple[str, ...]
    metadata_line_number: int


class Flattener:
    """
    Converts Transaction objects into a stream of normalized rows.

    Responsibilities:
    - Flatten hierarchical transaction structure
    - Maintain streaming behavior
    """

    def __init__(self) -> None:
        self._transaction_counter = 0

    def flatten(
        self, transactions: Iterable[Transaction]
    ) -> Generator[NormalizedRow, None, None]:
        """
        Flatten transactions into normalized rows.
        """

        for transaction in transactions:
            self._transaction_counter += 1
            txn_id = self._transaction_counter

            # Header
            if transaction.header:
                yield NormalizedRow(
                    transaction_id=txn_id,
                    record_type="HEADER",
                    fields=tuple(transaction.header.fields),
                    metadata_line_number=transaction.metadata.line_number,
                )

            # Details
            for detail in transaction.details:
                yield self._flatten_detail(txn_id, detail, transaction)

            # Payments
            for payment in transaction.payments:
                yield self._flatten_payment(txn_id, payment, transaction)

            # Trailer
            if transaction.trailer:
                yield NormalizedRow(
                    transaction_id=txn_id,
                    record_type="TRAILER",
                    fields=tuple(transaction.trailer.fields),
                    metadata_line_number=transaction.metadata.line_number,
                )

    def _flatten_detail(
        self, txn_id: int, detail: Detail, transaction: Transaction
    ) -> NormalizedRow:
        return NormalizedRow(
            transaction_id=txn_id,
            record_type="DETAIL",
            fields=tuple(detail.fields),
            metadata_line_number=transaction.metadata.line_number,
        )

    def _flatten_payment(
        self, txn_id: int, payment: Payment, transaction: Transaction
    ) -> NormalizedRow:
        return NormalizedRow(
            transaction_id=txn_id,
            record_type="PAYMENT",
            fields=tuple(payment.fields),
            metadata_line_number=transaction.metadata.line_number,
        )
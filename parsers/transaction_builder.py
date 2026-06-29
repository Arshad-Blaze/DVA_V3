from __future__ import annotations

import logging
from typing import Generator, List, Optional

from models import (
    Detail,
    Header,
    Metadata,
    ParserConfig,
    Payment,
    RecordRole,
    Trailer,
    Transaction,
)
from parsers.tokenizer import Token

logger = logging.getLogger(__name__)


class TransactionBuilder:
    """
    Builds Transaction objects from a stream of Tokens.

    Responsibilities:
    - Group tokens into transactions
    - Assign roles (header, detail, payment, trailer)
    - Emit Transaction objects in a streaming manner
    """

    def __init__(self, config: ParserConfig) -> None:
        self.config = config

    def build(
        self, tokens: Generator[Token, None, None]
    ) -> Generator[Transaction, None, None]:
        """
        Convert token stream into Transaction objects.
        """

        current_header: Optional[Header] = None
        current_details: List[Detail] = []
        current_payments: List[Payment] = []
        current_trailer: Optional[Trailer] = None
        metadata: Optional[Metadata] = None

        for token in tokens:
            role = self.config.get_role(token.record_type)

            # Start of new transaction
            if token.record_type == self.config.transaction.start_record:
                # Emit previous transaction if exists
                if current_details:
                    yield Transaction(
                        header=current_header,
                        details=current_details,
                        payments=current_payments,
                        trailer=current_trailer,
                        metadata=metadata,
                    )

                # Reset state
                current_header = None
                current_details = []
                current_payments = []
                current_trailer = None

            # Assign based on role
            if role == RecordRole.HEADER:
                current_header = Header(fields=token.fields)

                metadata = Metadata(
                    source_file="unknown",  # Will be enhanced later via pipeline
                    line_number=token.line_number,
                )

            elif role == RecordRole.DETAIL:
                current_details.append(Detail(fields=token.fields))

            elif role == RecordRole.PAYMENT:
                current_payments.append(Payment(fields=token.fields))

            elif role == RecordRole.TRAILER:
                current_trailer = Trailer(fields=token.fields)

            else:
                raise ValueError(f"Unhandled record role: {role}")

        # Emit last transaction
        if current_details:
            yield Transaction(
                header=current_header,
                details=current_details,
                payments=current_payments,
                trailer=current_trailer,
                metadata=metadata,
            )
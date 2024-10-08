from dataclasses import dataclass
from typing import Union


@dataclass
class Reversal:
    mpesa_code: str
    amount: Union[int, str]


@dataclass
class ReversalCallback:
    conversation_id: str
    originator_conversation_id: str
    result_code: Union[int, str]
    result_desc: str
    result_type: int
    transaction_id: str


@dataclass
class ReversalCallbackRequest:
    ConversationID: str
    OriginatorConversationID: str
    ResultCode: Union[int, str]
    ResultDesc: str
    ResultType: int
    TransactionID: str


@dataclass
class ReversalCallbackResult:
    Result: ReversalCallbackRequest


@dataclass
class TransactionStatusCallbackResult:
    Result: object

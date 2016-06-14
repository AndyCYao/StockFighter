"""Sixth Trade - making_amends.

    This will submit an evidence 
"""

from gamemaster import StockFighter as sF
import json


class SixthTradeSF(sF):
    """Implement my own socket for checking ids."""

    def __init__(self, level):
        sF.__init__(self, level)

    def submit_evidence(account, explanation_link, executive_summary):
        pass

trader = SixthTradeSF("making_amends")


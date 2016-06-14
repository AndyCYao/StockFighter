"""Sixth Trade - making_amends.

    This will submit an evidence 
"""

from gamemaster import StockFighter as sF
import json
import requests

class SixthTradeSF(sF):
    """Implement my own socket for checking ids."""

    def __init__(self, level):
        sF.__init__(self, level)

    def submit_evidence(self, evidenceJSON):
        header = {'X-Starfighter-Authorization': self.apikey}

        gm_url = "https://www.stockfighter.io/gm"
        full_url = "%s/instances/%s/judge" % (gm_url, 
                                              self.instanceID)
        response = requests.post(full_url, 
                                 headers = header,
                                 data = evidenceJSON)
        try:
            print response.text
            return response
        except ValueError as e:
            return{'error':e, 
                   'raw_content': response.content}

if __name__ == '__main__':
    trader = SixthTradeSF("making_amends")
    account = "MAD12044586"
    explanation_link = "https://github.com/AndyCYao/StockFighter"
    executive_summary = "This account has a much differ trading volumne than others. it made strategic high volumne trades unlike the others."

    evidence = {
        'account': account,
        'explanation_link': explanation_link, 
        'executive_summary': executive_summary,
        }

    evidenceJSON = json.dumps(evidence)
    print evidenceJSON
    trader.submit_evidence(evidenceJSON)

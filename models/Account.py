
import json

class Account:
    def __init__(self, wallet):
        """
        Example data


        wallet = "0x58507fed0Cb11723dFb6848c92C59Cf0BBEB9927"

        first_trans = {"CHAIN_NAME": "20-01-2023 12:10:55"}

        last_trans = {"CHAIN_NAME": "20-01-2023 12:10:55"}

        trans_count = {"CHAIN_NAME": 1}

        avg_time_trans = {"CHAIN_NAME": "30:12:43"}

        token_balance = {'CNAIN_NAME': [{'symbol': 'btc', 
        count: 10.34, 'in_usd': 22222}, ...]}

        nfts = {'CHAIN_NAME': [{'name': 'ok bears', 'count': 
        1, 'in_usd': 2134}, ...]}

        fee_pay = {'CHAIN_NAME': 'arb': {'count': 0.213, 
        'in_usd': 100}, ...}

        """
        self.wallet = wallet
        self.fist_trans = dict()
        self.last_trans = dict()
        self.trans_count = dict()
        self.avg_time_trans = dict()
        self.token_balance = dict()
        self.nfts = dict()
        self.fee_pay = dict()

    def ready(self):
        if (self.fist_trans and self.last_trans and self.trans_count
            and self.avg_time_trans and self.token_balance
                and self.nfts and self.fee_pay):
            return True
        return False

    def __str__(self):
        return f"wallet = {self.wallet}\nfirst_trans = {self.fist_trans}\nlast_trans = {self.last_trans}\ntrans_count= {self.trans_count}\navg_time_trans = {self.avg_time_trans}\ntoken_balance = {json.dumps(self.token_balance, indent=4)}\nnfts = {self.nfts}\nfee_pay = {self.fee_pay}"

    def __repr__(self):
        return f"\n{self.wallet}\n{self.fist_trans}\n{self.last_trans}\n{self.trans_count}\n{self.avg_time_trans}\n{self.token_balance}\n{self.nfts}\n{self.fee_pay}"


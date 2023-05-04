import datetime
import asyncio
import json

from models import Account, Chain
from core.transactions_info import get_accounts_transactions
from core.tokens import set_accounts_tokens
from core.nfts import set_accounts_nfts
from utils.tokens import get_ERCcontracts, zk_feepay_gen


async def accounts_init(wallets):
    ret_accounts = []
    print("Start initizlize accounts")
    trans = await get_accounts_transactions(wallets)
    print("All transctions scraped")
    for ind, addr in enumerate(wallets):
        account = Account.Account(addr)
        for chain in trans:
            if addr not in trans[chain]:
                continue
            account.trans_count[chain] = len(trans[chain][addr])
            # if addr == '0xdea3dbbe54013e59c6bfeaed2c6c9f720fa44cf1':
            #     print(ret_accounts[0].trans_count)
            if account.trans_count[chain] == 0:
                continue
            # print(trans[chain][addr][-1]['timeStamp'], chain, addr)
            f_trans = datetime.datetime.fromtimestamp(
                int(trans[chain][addr][-1]['timeStamp']))
            l_trans = datetime.datetime.fromtimestamp(
                int(trans[chain][addr][0]['timeStamp']))
            account.fist_trans[chain] = f_trans.strftime(
                "%d-%m-%Y %H:%M:%S")
            account.last_trans[chain] = l_trans.strftime(
                "%d-%m-%Y %H:%M:%S")
            s = (l_trans - f_trans).total_seconds() / account.trans_count[chain]
            hours, remainder = divmod(s, 3600)
            minutes, seconds = divmod(remainder, 60)
            account.avg_time_trans[chain] = '{:02}:{:02}:{:02}'.format(
                int(hours), int(minutes), int(seconds))
            account.fee_pay[chain] = {}
            if chain == Chain.ChainName.ZKSYNC:
                account.fee_pay[chain] = zk_feepay_gen(trans[chain][addr], addr)
            else:
                for tx in trans[chain][addr]:
                    if 'gasUsed' not in tx:
                        print(tx)
                account.fee_pay[chain]['wei'] = sum(
                    int(tx['gasUsed']) * int(tx['gasPrice']) for tx in trans[chain][addr] if tx['from'] == addr)
                account.fee_pay[chain]['count'] = account.fee_pay[chain]['wei'] / 10**18
        ret_accounts.append(account)
    return (ret_accounts, trans)


async def accounts_tokens_nfts_init(accounts, transactions):
    print("Start tokens & nfts collect")
    ERCcontracts = get_ERCcontracts(transactions)
    accounts, ERCcontracts, bad_Contracts = await set_accounts_tokens(accounts, ERCcontracts)
    ERCcontracts_clone = dict(ERCcontracts)
    while bad_Contracts != {}:
        # print(bad_Contracts)
        accounts, ERCcontracts, bad_Contracts = await set_accounts_tokens(accounts, bad_Contracts)
        ERCcontracts_clone.update(ERCcontracts)
    ERCcontracts = ERCcontracts_clone
    print("Tokens collect")
    return accounts

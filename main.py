
from telebot.async_telebot import AsyncTeleBot

import os
import asyncio
import json
import time

from core import initialization, gecko, excel, tokens
from models import Chain
from utils.gecko import token_list_ids, nft_list_ids

from core.scans import config as out_source_cfg
from core.scans import main as out_source_funcs


async def main():
    wallets = []
    accounts = []

    with open('wallets.txt', 'r') as file:
        wallets = file.read().split('\n')

    with open('json/сoin_gecko.json', 'rb') as file:
        tokens_info_ = json.loads(file.read().decode('utf8'))

    with open('json/nfts_gecko.json', 'rb') as file:
        nft_info_ = json.loads(file.read().decode('utf8'))

    with open('json/zk_tokens.json', 'rb') as file:
        zkTokensInfo = json.loads(file.read().decode('utf8'))

    for i, val in enumerate(wallets):
        wallets[i] = val.lower()    

    accounts, transactions = await initialization.accounts_init(wallets)

    accounts = await tokens.set_fee_prices(accounts)

    # SCRAPING TOKENS
    # accounts = await initialization.accounts_tokens_nfts_init(accounts, transactions)

    # tokens_ids = token_list_ids(accounts, tokens_info_) # {SYMBOL: "TOKEN_ID"}
    # for acc in accounts:
    #     print('\n', acc, '\n')
    # token_prices = await gecko.get_token_prices(tokens_ids)
    # token_prices = await tokens.zkTokenPrices(accounts, token_prices, zkTokensInfo)
    # accounts = gecko.set_token_prices(accounts, token_prices)

    # SCRAPING NFTS
    # contracts = nft_list_ids(accounts, nft_info_)
    # # print(contracts)
    # nft_prices = await gecko.get_nft_prices(contracts)
    # # print(nft_prices)
    # accounts = gecko.set_nft_prices(accounts, nft_prices)

    out_source = {}
    outs_CI = out_source_cfg.CHAINS_INFO
    for chain in outs_CI:
        print(f"STARTING PARSING {chain.upper()}")
        # print(out_source_funcs.get_wallets(
        #     "wallets.txt",
        #     outs_CI[chain],
        #     outs_CI[chain]["apikey"],
        #     outs_CI[chain]["file"],
        #     outs_CI[chain]["url"]
        # ))
        out_source[chain] = out_source_funcs.get_wallets("wallets.txt", "stark_wallets.txt", chain, outs_CI[chain]["apikey"], outs_CI[chain]["file"], outs_CI[chain]["url"])

    print(out_source)
    print("All data ready")

    try:
        excel.create_tables_by_accounts(accounts, out_source, 'Out')
    except Exception as e:
        print("Cant open file", e)

if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    print(f"{int(time.time() - start_time)} seconds working")
# 0.00460092027532 0xd9ffaf2e880df0cc7b7104e9e789d281a81824cf


from telebot.async_telebot import AsyncTeleBot

import os
import asyncio
import json
import time

from core import initialization, gecko, excel, tokens
from models import Chain
from utils.gecko import token_list_ids, nft_list_ids

bot = AsyncTeleBot('2053206737:AAHyNExom0kRgUhxE_QhYGl_Y0AKCdh8lG4')

with open('json/сoin_gecko.json', 'rb') as file:
    tokens_info_ = json.loads(file.read().decode('utf8'))

with open('json/nfts_gecko.json', 'rb') as file:
    nft_info_ = json.loads(file.read().decode('utf8'))


with open('json/zk_tokens.json', 'rb') as file:
    zkTokensInfo = json.loads(file.read().decode('utf8'))


@bot.message_handler(commands=['start'])
async def handle_start(msg):
    await bot.send_message(chat_id=msg.chat.id, text=f"Hello\nIt's bot for check fees in Ethereum, Optimism, Arbitrum, Fantom, Polygon chains")


@bot.message_handler(commands=['help'])
async def handle_help(msg):
    await bot.send_message(chat_id=msg.chat.id, text=f"For check fees send wallets, one wallet per line(limit=50). Example:\n0xa1d85ed87fb34938ee6af2869722ebfe66d34c1d\n0x9f3be1a81c8d5f284ea1994ea3692b15552dd8ac")


@bot.message_handler()
async def main_handler(msg):
    wallets_bad = msg.json['text'].split('\n')
    wallets = []

    for ind, wallet in enumerate(wallets_bad):
        if len(wallet) == 42 and wallet[:2] == '0x':
            wallets.append(wallet.lower())

    for i, val in enumerate(wallets):
        wallets[i] = val.lower()

    wallets = wallets[:50]

    await bot.send_message(chat_id=msg.chat.id, text='Wallets handling:\n{}'.format("\n".join(wallets)))

    accounts, transactions = await initialization.accounts_init(wallets)

    accounts = await tokens.set_fee_prices(accounts)

    accounts = await initialization.accounts_tokens_nfts_init(accounts, transactions)

    tokens_ids = token_list_ids(accounts, tokens_info_)  # {SYMBOL: "TOKEN_ID"}
    for acc in accounts:
        print('\n', acc, '\n')
    token_prices = await gecko.get_token_prices(tokens_ids)
    token_prices = await tokens.zkTokenPrices(accounts, token_prices, zkTokensInfo)
    accounts = gecko.set_token_prices(accounts, token_prices)

    # contracts = nft_list_ids(accounts, nft_info_)
    # # print(contracts)
    # nft_prices = await gecko.get_nft_prices(contracts)
    # # print(nft_prices)
    # accounts = gecko.set_nft_prices(accounts, nft_prices)

    file_name = f"tables/{str(msg.chat.id)}"
    try:
        excel.create_tables_by_accounts(accounts, file_name)
    except:
        print("Cant open file")

    try:
        with open(f"{file_name}.xlsx", 'rb') as cur_table:
            print('Try file send')
            await bot.send_document(msg.chat.id, cur_table)
            print('File sended')

        if os.path.exists(f"tables/{str(msg.chat.id)}.xlsx"):
            os.remove(f"tables/{str(msg.chat.id)}.xlsx")

    except Exception as e:
        print('Error in send table or del.\n', e)


asyncio.run(bot.infinity_polling())

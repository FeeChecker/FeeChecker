from asyncio import sleep

import aiohttp
import datetime

from models import Chain

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 80, fill = '█', printEnd = "\r"):
    if total == 0:
        return
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix[:15]}', end = printEnd)
    if iteration == total: 
        print()

async def get_all_transactions_by_addr_zksync(session, addr):
    from_find = 'latest'
    transactions = []
    transactions_count = 1  # 1 for start loop
    while len(transactions) < transactions_count:
        async with session.get(Chain.TransactionByAccount.ZKSYNC.format(addr, from_find)) as resp:
            json_data = await resp.json()
            if json_data['status'] == 'success':
                json_data = json_data['result']
                transactions_count = json_data['pagination']['count']
                if from_find != 'latest':
                    json_data['list'] = json_data['list'][1:]
                for ind, tx in enumerate(json_data['list']):
                    json_data['list'][ind]['timeStamp'] = datetime.datetime.timestamp(
                    	datetime.datetime.strptime(
                        tx['createdAt'], '%Y-%m-%dT%H:%M:%S.%fZ'))
                transactions.extend(json_data['list'])
                # print(len(transactions))
                from_find = json_data['pagination']['from']
        await sleep(0.5)
    return transactions


async def get_accounts_transactions(wallets):
    w_count = len(wallets) - 1
    transactions = {}  # {'CHAIN_NAME': {'ADDRESS': [tx1, tx2, ...]}, ...}
    async with aiohttp.ClientSession() as session:
        for w_ind, addr in enumerate(wallets):
            printProgressBar(w_ind, w_count, suffix=addr)
            # ARBITRUM_NOVA disable API
            # try:
            # 	async with session.get(Chain.TransactionByAccount.ARBITRUM_NOVA + addr) as resp:
            # 		json_data = await resp.json()
            # 		if json_data['message'] == 'OK':
            # 			transactions[Chain.ChainName.ARBITRUM_NOVA] = json_data['result']
            # except Exception as e:
            # 	print(f"Error in get_accounts_transactions ARBITRUM_NOVA\n{e}")
            # ARBITRUM
            try:
                async with session.get(Chain.TransactionByAccount.ARBITRUM + addr) as resp:
                    json_data = await resp.json()
                    if json_data['message'] == 'OK':
                        if Chain.ChainName.ARBITRUM not in transactions:
                            transactions[Chain.ChainName.ARBITRUM] = {}
                        transactions[Chain.ChainName.ARBITRUM][addr] = json_data['result']
            except Exception as e:
                print(f"Error in get_accounts_transactions ARBITRUM\n{e}")
            # ETHEREUM
            try:
                async with session.get(Chain.TransactionByAccount.ETHEREUM + addr) as resp:
                    json_data = await resp.json()
                    if json_data['message'] == 'OK':
                        if Chain.ChainName.ETHEREUM not in transactions:
                            transactions[Chain.ChainName.ETHEREUM] = {}
                        transactions[Chain.ChainName.ETHEREUM][addr] = json_data['result']
            except Exception as e:
                print(f"Error in get_accounts_transactions ETHEREUM\n{e}")
            # POLYGON
            try:
                async with session.get(Chain.TransactionByAccount.POLYGON + addr) as resp:
                    json_data = await resp.json()
                    if json_data['message'] == 'OK':
                        if Chain.ChainName.POLYGON not in transactions:
                            transactions[Chain.ChainName.POLYGON] = {}
                        transactions[Chain.ChainName.POLYGON][addr] = json_data['result']
            except Exception as e:
                print(f"Error in get_accounts_transactions POLYGON\n{e}")
            # FANTOM
            try:
                async with session.get(Chain.TransactionByAccount.FANTOM + addr) as resp:
                    json_data = await resp.json()
                    if json_data['message'] == 'OK':
                        if Chain.ChainName.FANTOM not in transactions:
                            transactions[Chain.ChainName.FANTOM] = {}
                        transactions[Chain.ChainName.FANTOM][addr] = json_data['result']
            except Exception as e:
                print(f"Error in get_accounts_transactions FANTOM\n{e}")
            # OPTIMISM
            try:
                async with session.get(Chain.TransactionByAccount.OPTIMISM + addr) as resp:
                    json_data = await resp.json()
                    if json_data['message'] == 'OK':
                        if Chain.ChainName.OPTIMISM not in transactions:
                            transactions[Chain.ChainName.OPTIMISM] = {}
                        transactions[Chain.ChainName.OPTIMISM][addr] = json_data['result']
            except Exception as e:
                print(f"Error in get_accounts_transactions OPTIMISM\n{e}")
            # BSC
            try:
                async with session.get(Chain.TransactionByAccount.BSC + addr) as resp:
                    json_data = await resp.json()
                    if json_data['message'] == 'OK':
                        if Chain.ChainName.BSC not in transactions:
                            transactions[Chain.ChainName.BSC] = {}
                        transactions[Chain.ChainName.BSC][addr] = json_data['result']
            except Exception as e:
                print(f"Error in get_accounts_transactions BSC\n{e}")
            # ZKSYNC
            try:
                json_data = await get_all_transactions_by_addr_zksync(session, addr)
                if Chain.ChainName.ZKSYNC not in transactions:
                    transactions[Chain.ChainName.ZKSYNC] = {}
                transactions[Chain.ChainName.ZKSYNC][addr] = json_data
            except Exception as e:
                print(f"Error in get_accounts_transactions ZKSYNC\n{e}")
    return transactions

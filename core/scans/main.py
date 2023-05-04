import datetime
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup
from loguru import logger

if __name__ == "__main__":
    from config import CHAINS_INFO, wallet_file
else:
    from core.scans.config import CHAINS_INFO, wallet_file
# logger.add("log/debug.log").


def get_transactions(wallet, apikey, url):
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "module": "account",
        "action": "txlist",
        "address": wallet,
        "startblock": 0,
        "endblock": 99999999,
        "page": 1,
        "offset": 1000,
        "sort": "asc",
        "apikey": apikey,
    }

    res = requests.post(url, data, headers)
    return res.json()


def parse_starknet(wallet):
    page = 1

    result = []

    attempt = 0
    transactions = None
    while attempt < 3:
        try:
            url = f"https://voyager.online/api/txns?to={wallet}&ps=50&p={page}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"}
            res = requests.get(url, headers)
            res = res.json()
            logger.info(f"STARKNET REQUEST ATTEMPT: {attempt}")
            transactions = res["items"]
            break
        except:
            logger.error(f"Error in starknet: {res['message']}")
            if attempt < 3:
                logger.info("Retry request")
                attempt += 1
            else:
                logger.error("RETRY FAILED")
                result.append(0)
                return result

    if (transactions):
        total_transactions = len(transactions)
    else:
        total_transactions = 0

    if total_transactions == 0:
        result.append(total_transactions)
        return result

    if res["lastPage"] > 1:

        for i in range(2, res["lastPage"] + 1):
            page = i
            url = f"https://voyager.online/api/txns?to={wallet}&ps=50&p={page}"
            res = requests.get(url)
            res = res.json()
            if ("items" in res):
                transactions.extend(res["items"])
            else:
                return [0]
                print(res)

    total_transactions = len(transactions)
    result.append(total_transactions)
    first_transaction_time = datetime.datetime.fromtimestamp(
        int(transactions[total_transactions - 1]["timestamp"])
    ).strftime("%d-%m-%Y %H:%M:%S")
    result.append(first_transaction_time)

    last_transaction_time = datetime.datetime.fromtimestamp(
        int(transactions[0]["timestamp"])
    ).strftime("%d-%m-%Y %H:%M:%S")
    result.append(last_transaction_time)

    AVG_time = get_average_time(get_times(transactions, "starknet"))
    result.append(AVG_time)

    fee_token = get_gas_ETH(transactions, "starknet")
    result.append(fee_token)

    fee_usd = get_gas_USD(fee_token)
    result.append(fee_usd)

    return result


def get_times(transactions, chain=False):
    unix_times = []
    for _dict in transactions:
        if not chain:
            unix_times.append(int(_dict["timeStamp"]))
        else:
            unix_times.append(int(_dict["timestamp"]))
    return unix_times


def get_average_time(unix_times):

    average_time = sum(unix_times) / len(unix_times)
    average_time = datetime.datetime.fromtimestamp(int(average_time))
    time_str = average_time.strftime("%H:%M:%S")
    return time_str


def get_arbitrum_price(txhash, chain):
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"}

    if chain == 'arbitrum_nova':
        res = requests.get(f"https://nova.arbiscan.io/tx/{txhash}", headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        gas_actual_price = soup.find('span', attrs={'title': "Actual Gas Price * Gas Used by Transaction"})
    else:
        res = requests.get(f"https://optimistic.etherscan.io/tx/{txhash}", headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        gas_actual_price = soup.find('span', attrs={'data-toggle': "tooltip", 'title': "(Gas Price * Gas) + (l1GasUsed * l1GasPrice * l1FeeScalar)"})

    # if (not gas_actual_price):
    #     print(soup)
    if (not gas_actual_price):
        gas_actual_price = '0'
    else:
        gas_actual_price = gas_actual_price.get_text()

    temp_arr = gas_actual_price.split()

    gasprice = float(temp_arr[0]) / 1e-18

    return gasprice


def get_gas_ETH(transactions, chain=False):
    gas_wei_trans = []
    for _dict in transactions:

        if chain == 'optimism':
            gas_wei_trans.append(
                int(get_arbitrum_price(_dict['hash'], chain)))
        elif chain == 'starknet':
            gas_wei_trans.append(int(_dict["actual_fee"]))
        else:
            gas_wei_trans.append(int(get_arbitrum_price(_dict['hash'], chain)))

    total_wei = sum(gas_wei_trans)
    wei_to_eth = 1e-18
    return total_wei * wei_to_eth


def get_gas_USD(eth_price):
    url = "https://api.coinbase.com/v2/prices/ETH-USD/spot"
    response = requests.get(url)
    data = response.json()
    eth_to_usd = float(data["data"]["amount"])

    return eth_price * eth_to_usd


def parse_response(res, chain):
    result = []

    transactions = res["result"]
    total_transactions = len(transactions)
    result.append(total_transactions)
    if total_transactions == 0:
        return result

    first_transaction_time = datetime.datetime.fromtimestamp(
        int(transactions[0]["timeStamp"])
    ).strftime("%d-%m-%Y %H:%M:%S")
    result.append(first_transaction_time)

    last_transaction_time = datetime.datetime.fromtimestamp(
        int(transactions[total_transactions - 1]["timeStamp"])
    ).strftime("%d-%m-%Y %H:%M:%S")
    result.append(last_transaction_time)

    AVG_time = get_average_time(get_times(transactions))
    result.append(AVG_time)

    fee_token = get_gas_ETH(transactions, chain)
    result.append(fee_token)

    fee_usd = get_gas_USD(fee_token)
    result.append(fee_usd)

    return result


def get_csv(info, csv_file):
    data = {
        "Wallet": [],
        "Transaction count": [],
        "First trans UTC": [],
        "Last trans UTC": [],
        "AVG trans time": [],
        "Fee(token)": [],
        "Fee(USD)": [],
    }
    for arr in info:
        if len(arr) != 2:
            data["Wallet"].append(arr[len(arr) - 1])
            data["Transaction count"].append(arr[0])
            data["First trans UTC"].append(arr[1])
            data["Last trans UTC"].append(arr[2])
            data["AVG trans time"].append(arr[3])
            data["Fee(token)"].append(arr[4])
            data["Fee(USD)"].append(arr[5])
        else:
            data["Wallet"].append(arr[len(arr) - 1])
            data["Transaction count"].append(0)
            data["First trans UTC"].append(0)
            data["Last trans UTC"].append(0)
            data["AVG trans time"].append(0)
            data["Fee(token)"].append(0)
            data["Fee(USD)"].append(0)

    df = pd.DataFrame(data)
    df.to_csv(csv_file, index=False)
    logger.info("Csv created")


def get_wallets(file, stark_file, chain, apikey, csv_file, url):
    with open(file) as f:
        wallets = f.readlines()

    with open(stark_file) as f:
        stark_wallets = f.readlines()

    all_wallets_info = []
    i = 1
    logger.info(f"The beginning of parsing. Count of wallet: {len(wallets)}")
    for wallet in wallets:
        wallet = wallet.replace("\n", "")
        logger.info(
            f"Parse wallet: {wallet}. Left: {len(wallets) - i} wallets")
        if chain != "starknet":
            res = get_transactions(wallet, apikey, url)
            wallet_info = parse_response(res, chain)
            wallet_info.append(wallet)
            all_wallets_info.append(wallet_info)
        i += 1

    for wallet in stark_wallets:
        wallet = wallet.replace("\n", "")
        logger.info(
            f"Parse wallet: {wallet}. Left: {len(stark_wallets) - i} wallets")
        if chain == "starknet":
            wallet_info = parse_starknet(wallet)
            wallet_info.append(wallet)
            all_wallets_info.append(wallet_info)
            
        i += 1

    logger.info(f"The end of parsing. Creating csv...")
    # get_csv(all_wallets_info, csv_file)
    return (all_wallets_info)


if __name__ == "__main__":
    for chain in CHAINS_INFO.items():
        logger.info(f"STARTING PARSING {chain[0].upper()}")
        print(get_wallets(
            wallet_file, 'stark_wallets.txt', chain[0], chain[1]["apikey"], chain[1]["file"], chain[1]["url"]
        ))

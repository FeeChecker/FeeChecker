import aiohttp

from models import Chain


async def get_token_prices(token_ids):
    async with aiohttp.ClientSession() as session:
        url = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page=1&sparkline=false&ids='
        url += "%2C".join(token_ids[symbol]['id'] for symbol in token_ids)

        async with session.get(url) as resp:
            try:
                json_data = await resp.json()
                print(len(json_data))
                for token in json_data:
                    try:
                        token_ids[token['symbol']
                                  ]['price'] = token['current_price']
                    except:
                        print(
                            f"{token['symbol']} token have not current_price")
            except Exception as e:
                print(e)
                print('Need len =', len(token_ids),
                      ', recv len =', len(json_data))
                print('Coingecko not give token prices')
    return token_ids


def set_token_prices(accounts, token_prices):
    symbols = [sy for sy in token_prices]
    for ind, acc in enumerate(accounts):
        for chain_name in acc.token_balance:
            try:
                if chain_name == Chain.ChainName.ZKSYNC:
                    for zk_tok in acc.token_balance[chain_name]:
                        if zk_tok in token_prices:
                            cur_token = acc.token_balance[chain_name][zk_tok]
                            accounts[ind].token_balance[chain_name][zk_tok]['count'] = cur_token['wei'] / 10**token_prices[zk_tok]['decimals']
                            accounts[ind].token_balance[chain_name][zk_tok]['in_usd'] = token_prices[zk_tok]['price'] * cur_token['count']
                    # for zk_tok in zk_tokens:
                    #     async with session.get(Chain.TokenPrices.ZK.format(zk_tok)) as resp:
                    #         json_data = await resp.json()
                    #         zk_tokens_prices[zk_tok] = {}
                    #         zk_tokens_prices[zk_tok]['price'] = float(json_data['result']['price'])
                    #         zk_tokens_prices[zk_tok]['decimals'] = json_data['result']['decimals']
                    #         zk_tokens_prices[zk_tok]['symbol'] = json_data['result']['tokenSymbol']
                    # for tok_id in acc.token_balance[chain_name]:
                    #     print(acc.token_balance[chain_name][tok_id])
                    #     acc_symbol = acc.token_balance[chain_name][tok_id]['symbol']
                    #     if acc_symbol in symbols:
                    #         accounts[ind].token_balance[chain_name][tok_id]['in_usd'] = acc.token_balance[chain_name][tok_id]['count'] * next(
                    #             token_prices[g] for g in token_prices if g == acc_symbol)['price']
                else:
                    for token_name in acc.token_balance[chain_name]:
                        if 'symbol' not in acc.token_balance[chain_name][token_name]:
                            acc_symbol = token_name
                        else:
                            acc_symbol = acc.token_balance[chain_name][token_name]['symbol'].lower(
                        )
                        if acc_symbol in symbols:
                            accounts[ind].token_balance[chain_name][token_name]['in_usd'] = acc.token_balance[chain_name][token_name]['count'] * next(
                                token_prices[g] for g in token_prices if g == acc_symbol)['price']
            except Exception as e:
                print(f"\nError\n{acc_symbol} {chain_name}\n{e}")

    ETH_FEE = [
        Chain.ChainName.ARBITRUM,
        Chain.ChainName.OPTIMISM,
        Chain.ChainName.ETHEREUM,
        Chain.ChainName.BSC]

    FTM_FEE = [Chain.ChainName.FANTOM]

    MATIC_FEE = [Chain.ChainName.POLYGON]

    ETH_price = next(token_prices[g]
                     for g in token_prices if g == 'eth')['price']
    FTM_price = next(token_prices[g]
                     for g in token_prices if g == 'ftm')['price']
    MATIC_price = next(token_prices[g]
                       for g in token_prices if g == 'matic')['price']
    for ind, acc in enumerate(accounts):
        for chain_name in acc.fee_pay:
            if chain_name in ETH_FEE:
                accounts[ind].fee_pay[chain_name]['in_usd'] = acc.fee_pay[chain_name]['count'] * ETH_price
            if chain_name in FTM_FEE:
                accounts[ind].fee_pay[chain_name]['in_usd'] = acc.fee_pay[chain_name]['count'] * FTM_price
            if chain_name in MATIC_FEE:
                accounts[ind].fee_pay[chain_name]['in_usd'] = acc.fee_pay[chain_name]['count'] * MATIC_price

    return accounts


async def get_nft_prices(contracts):
    ret_contracts = {}
    async with aiohttp.ClientSession() as session:
        for con in contracts:
            try:
                url = "https://api.coingecko.com/api/v3/nfts/" + \
                    contracts[con]['id']
                async with session.get(url) as resp:
                    json_data = await resp.json()
                    ret_contracts[con] = json_data['floor_price']['usd']
            except:
                print(f"Did not receive a response by {con}")

    return ret_contracts


def set_nft_prices(accounts, nft_prices):
    for ind, acc in enumerate(accounts):
        for chain_name in acc.nfts:
            for nft_name in acc.nfts[chain_name]:
                if 'contractAddress' not in acc.nfts[chain_name][nft_name]:
                    continue
                if acc.nfts[chain_name][nft_name]['contractAddress'] in nft_prices:
                    accounts[ind].nfts[chain_name][nft_name]['in_usd'] = acc.nfts[chain_name][nft_name]['count'] * \
                        nft_prices[acc.nfts[chain_name]
                                   [nft_name]['contractAddress']]

    return accounts

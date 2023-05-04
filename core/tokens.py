import aiohttp
import json

from asyncio import sleep

from models import Chain
from utils.tokens import tokens_from_transactions


async def set_accounts_tokens(accounts, ERCcontracts):
    ret_ERCcontracts = {}
    bad_ERCcontracts = {}
    async with aiohttp.ClientSession() as session:
        # ZKSYNC Tokens and NFTS
        for ind, acc in enumerate(accounts):
            try:
                async with session.get(Chain.TokensByAccount.ZKSYNC.format(acc.wallet)) as resp:
                    json_data = await resp.json()
                    if json_data['result'] is None:
                        continue
                    tokens_ = json_data['result']['balances']
                    accounts[ind].token_balance[Chain.ChainName.ZKSYNC] = {}
                    for symbol in tokens_:
                        custom_token = {}
                        custom_token['wei'] = int(tokens_[symbol])
                        # custom_token['count'] = custom_token['wei'] / 10**18
                        accounts[ind].token_balance[Chain.ChainName.ZKSYNC][symbol] = custom_token
                    nfts_ = json_data['result']['mintedNfts']
                    accounts[ind].nfts[Chain.ChainName.ZKSYNC] = {}
                    for inc in nfts_:
                        custom_nft = {}
                        custom_nft['count'] = 1
                        custom_nft['in_usd'] = 0
                        accounts[ind].nfts[Chain.ChainName.ZKSYNC][nfts_[inc]['symbol']] = custom_token
            except Exception as e:
                print(
                    f"Error in first part set_accounts_tokens {Chain.ChainName.ZKSYNC}\n{e}")
        # Other chians

        for chain_name in ERCcontracts:
            try:
                for ind, acc in enumerate(accounts):
                    if acc.wallet in ERCcontracts[chain_name]:
                        url = Chain.TokensTransByAddrContract().get_by_chain_name(chain_name)
                        for addressContract in ERCcontracts[chain_name][acc.wallet]:
                            if not addressContract:
                                continue
                            async with session.get(url.format(addressContract, acc.wallet)) as resp:
                                try:
                                    json_data = await resp.json()
                                    if json_data['message'] == 'No transactions found':
                                        if chain_name not in ret_ERCcontracts:
                                            ret_ERCcontracts[chain_name] = {}
                                        if acc.wallet not in ret_ERCcontracts[chain_name]:
                                            ret_ERCcontracts[chain_name][acc.wallet] = [
                                            ]
                                        ret_ERCcontracts[chain_name][acc.wallet].append(
                                            addressContract)
                                    else:
                                        # print(addressContract)
                                        token = await tokens_from_transactions(json_data['result'], acc.wallet, addressContract, session, chain_name)
                                        if chain_name not in accounts[ind].token_balance:
                                            accounts[ind].token_balance[chain_name] = {
                                            }
                                        accounts[ind].token_balance[chain_name].update(
                                            token)
                                except Exception as e:
                                    print(f'Exception for bad_ERCcontracts\n{e}')
                                    if chain_name not in bad_ERCcontracts:
                                        bad_ERCcontracts[chain_name] = {}
                                    if acc.wallet not in bad_ERCcontracts[chain_name]:
                                        bad_ERCcontracts[chain_name][acc.wallet] = [
                                        ]
                                    bad_ERCcontracts[chain_name][acc.wallet].append(
                                        addressContract)
                                    await sleep(5)

            except Exception as e:
                print(f"Error in last part set_accounts_tokens {chain_name}\n{e}")
    return (accounts, ret_ERCcontracts, bad_ERCcontracts)

async def set_fee_prices(accounts):
    async with aiohttp.ClientSession() as session:
        async with session.get(Chain.TokenPrices.ETH) as resp:
            json_data = await resp.json()
            ETH_price = float(json_data['result']['ethusd'])
        async with session.get(Chain.TokenPrices.MATIC) as resp:
            json_data = await resp.json()
            MATIC_price = float(json_data['result']['maticusd'])
        async with session.get(Chain.TokenPrices.FTM) as resp:
            json_data = await resp.json()
            FTM_price = float(json_data['result']['ethusd'])

        eth_chains = [
            Chain.ChainName.ETHEREUM,
            Chain.ChainName.ARBITRUM,
            Chain.ChainName.OPTIMISM,
            Chain.ChainName.BSC]

        zk_tokens = []
        for ind, acc in enumerate(accounts):
            for fee_chain in acc.fee_pay:
                if fee_chain in eth_chains:
                    accounts[ind].fee_pay[fee_chain]['in_usd'] = ETH_price * acc.fee_pay[fee_chain]['count']
                if fee_chain == Chain.ChainName.FANTOM:
                    accounts[ind].fee_pay[fee_chain]['in_usd'] = FTM_price * acc.fee_pay[fee_chain]['count']
                if fee_chain == Chain.ChainName.POLYGON:
                    accounts[ind].fee_pay[fee_chain]['in_usd'] = MATIC_price * acc.fee_pay[fee_chain]['count']

                if fee_chain == Chain.ChainName.ZKSYNC:
                    zk_tokens.extend(list(acc.fee_pay[fee_chain].keys()))

        zk_tokens = list(set(zk_tokens))

        zk_tokens_prices = {}
        for zk_tok in zk_tokens:
            async with session.get(Chain.TokenPrices.ZK.format(zk_tok)) as resp:
                json_data = await resp.json()
                zk_tokens_prices[zk_tok] = {}
                zk_tokens_prices[zk_tok]['price'] = float(json_data['result']['price'])
                zk_tokens_prices[zk_tok]['decimals'] = json_data['result']['decimals']
                zk_tokens_prices[zk_tok]['symbol'] = json_data['result']['tokenSymbol']

        for ind, acc in enumerate(accounts):
            if Chain.ChainName.ZKSYNC in acc.fee_pay:
                for zk_tok_id in acc.fee_pay['zk']:
                    accounts[ind].fee_pay['zk'][zk_tok_id]['count'] = acc.fee_pay['zk'][zk_tok_id]['wei'] / 10**zk_tokens_prices[zk_tok_id]['decimals']
                    accounts[ind].fee_pay['zk'][zk_tok_id]['in_usd'] = acc.fee_pay['zk'][zk_tok_id]['count'] * zk_tokens_prices[zk_tok_id]['price']
                    accounts[ind].fee_pay['zk'][zk_tok_id]['symbol'] = zk_tokens_prices[zk_tok_id]['symbol']


    return accounts

async def zkTokenPrices(accounts, token_prices, zkTokensInfo):
    zk_tokens = []
    for ind, acc in enumerate(accounts):
        if Chain.ChainName.ZKSYNC in acc.token_balance:
            zk_tokens.extend( list(acc.token_balance[Chain.ChainName.ZKSYNC].keys()) )
    zk_tokens_symbols = list(set(zk_tokens))
    zk_tokens = []

    for tk in zkTokensInfo:
        if tk['symbol'] in zk_tokens_symbols:
            zk_tokens.append(tk['id'])

    print("Zk tokens =", zk_tokens)

    zk_tokens_prices = {}
    async with aiohttp.ClientSession() as session:
        for zk_tok in zk_tokens:
            async with session.get(Chain.TokenPrices.ZK.format(zk_tok)) as resp:
                json_data = await resp.json()
                zk_tok_sym = json_data['result']['tokenSymbol']
                zk_tokens_prices[zk_tok_sym] = {}
                zk_tokens_prices[zk_tok_sym]['price'] = float(json_data['result']['price'])
                zk_tokens_prices[zk_tok_sym]['decimals'] = json_data['result']['decimals']

    token_prices.update(zk_tokens_prices)
    print(json.dumps(token_prices, indent=3))
    return token_prices
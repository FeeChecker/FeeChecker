from models import Chain

import json

def zk_feepay_gen(trans, addr):
    zk_fees = {} # {tokenId: {'wei': 1234, 'count': 1.234, 'in_usd': 0.3, 'symbol': 'HUI'}}
    for tx in trans:
        if 'from' not in tx['op'] and 'submitterAddress' not in tx['op'] and tx['op']['type'] != 'ChangePubKey':
            continue
        if tx['op']['type'] != 'ChangePubKey' and tx['op']['type'] != 'Swap':
            if tx['op']['from'] != addr:
                continue
        if 'feeToken' in tx['op']:
            tokId = tx['op']['feeToken']
        else:
            tokId = 0
        if tokId not in zk_fees:
            zk_fees[tokId] = {'wei': 0}
        if 'fee' in tx['op']:
            zk_fees[tokId]['wei'] += int(tx['op']['fee'])
    return zk_fees


async def tokens_from_transactions(transactions, addr, c_addr, session, chain_name):
    tokens = {}
    tName = transactions[0]['tokenName']
    symbol = transactions[0]['tokenSymbol']
    tokens[tName] = {}
    url = Chain.TokensWeiByAddrContract().get_by_chain_name(chain_name)
    # print(url.format(c_addr, addr))
    for _ in range(5):
        async with session.get(url.format(c_addr, addr)) as resp:
            try:
                json_data = await resp.json()
                if json_data['message'] != 'OK':
                    # print(json_data)
                    raise Exception('Tokens count not found')
                tokens[tName]['wei'] = int(json_data['result'])
                tokens[tName]['count'] = int(json_data['result']) / 10 ** int(transactions[0]['tokenDecimal'])
                tokens[tName]['symbol'] = symbol
                # print(chain_name, tokens)
                return tokens
            except:
                pass
    # symbol = transactions[0]['tokenName']
    # tokens[symbol] = {'wei': int(
    #     transactions[0]['value']), "symbol": transactions[0]['tokenSymbol']}
    # for tx in transactions[1:]:
    #     if tx['from'] == addr:
    #         tokens[symbol]['wei'] -= int(tx['value'])
    #     else:
    #         tokens[symbol]['wei'] += int(tx['value'])
    # tokens[symbol]['count'] = tokens[symbol]['wei'] / \
    #     10**int(transactions[0]['tokenDecimal'])


async def nfts_from_transactions(transactions, addr):
    nft = {}
    name_ = transactions[0]['tokenName']
    nft[name_] = {'contractAddress': transactions[0]['contractAddress']}
    c = []
    for tx in transactions:
        if tx['tokenID'] in c and tx['from'] == addr:
            del(c[c.index(tx['tokenID'])])
        else:
            c.append(tx['tokenID'])
    nft[name_]['count'] = len(c)
    return nft

def merge_accounts(base_accs, m_accs):
    for i, acc in enumerate(base_accs):
        for m_acc in m_accs:
            if m_acc.wallet == acc.wallet:
                if Chain.ChainName.POLYGON in m_acc.fist_trans:
                    base_accs[i].fist_trans[Chain.ChainName.POLYGON] = m_acc.fist_trans[Chain.ChainName.POLYGON]

                    base_accs[i].last_trans[Chain.ChainName.POLYGON] = m_acc.last_trans[Chain.ChainName.POLYGON]

                    base_accs[i].trans_count[Chain.ChainName.POLYGON] = m_acc.trans_count[Chain.ChainName.POLYGON]

                    base_accs[i].avg_time_trans[Chain.ChainName.POLYGON] = m_acc.avg_time_trans[Chain.ChainName.POLYGON]

                    base_accs[i].fee_pay[Chain.ChainName.POLYGON] = m_acc.fee_pay[Chain.ChainName.POLYGON]

    return (base_accs)
                

def get_ERCcontracts(transactions):
    ERCcontracts = {}
    for chain in transactions:
        if chain == Chain.ChainName.ZKSYNC:
            continue
        for addr in transactions[chain]:
            for tx in transactions[chain][addr]:
                if tx['functionName'] != "":
                    addressContract = tx['to']
                    if chain not in ERCcontracts:
                        ERCcontracts[chain] = {}
                    if addr in ERCcontracts[chain]:
                        if not tx['to']:
                            continue
                        ERCcontracts[chain][addr].append(tx['to'])
                    else:
                        ERCcontracts[chain][addr] = [tx['to']]
            try:
                ERCcontracts[chain][addr] = list(set(ERCcontracts[chain][addr]))
            except Exception as e:
                print(f'ERROR\n{e}')
                # print(ERCcontracts)
    return ERCcontracts

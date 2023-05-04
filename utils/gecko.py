import json

def token_list_ids(accounts, tokens_info_):
	token_symblos = []
	for acc in accounts:
		for chain_name in acc.token_balance:	
			for token_name in acc.token_balance[chain_name]:
				if 'symbol' in acc.token_balance[chain_name][token_name]:
					token_symblos.append(acc.token_balance[chain_name][token_name]['symbol'])

	token_ids = {}
	for symbol_ in token_symblos:
		l_symbol_ = symbol_.lower()
		for i, val in enumerate(tokens_info_):
			if val['symbol'] == l_symbol_:
				token_ids[val['symbol']] = {'id': val['id']}
				break

	# tokens for fees
	token_ids['eth'] = {'id': 'ethereum'}
	token_ids['ftm'] = {'id': 'fantom'}
	token_ids['matic'] = {'id': 'matic-network'}

	print(f'Started len token_ids', len(token_ids))

	return token_ids

def nft_list_ids(accounts, nft_info_):
	contracts = {}
	for acc in accounts:
		for chain_name in acc.nfts:
			for nft_name in acc.nfts[chain_name]:
				if 'contractAddress' not in acc.nfts[chain_name][nft_name]:
					continue
				contracts[acc.nfts[chain_name][nft_name]['contractAddress']] = {}

	for nft in nft_info_:
		try:
			if nft['contract_address'].lower() in contracts:
				contracts[nft['contract_address'].lower()]['id'] = nft['id']
		except:
			pass

	ret  = {}
	for cont in contracts:
		if 'id' in contracts[cont]:
			ret[cont] = contracts[cont]

	return ret
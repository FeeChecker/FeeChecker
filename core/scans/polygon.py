from bs4 import BeautifulSoup
import requests
import datetime

from models.Account import Account
from models import Chain

def get_res_page_txs(address: str, page: int = 1):
	URL = 'https://polygonscan.com/txs?a={}&p={}'
	return requests.get( URL.format(address, page) )

def get_wallet_txs_by_page(res: requests.Response):
	soup = BeautifulSoup(res.text)
	table = soup.find('table', {'class': 'table table-hover'})

	txs = []
	for tTx in table.tbody:
		if tTx == '\n':
			continue

		tx = {'fee': {}}
		tx['time'] = tTx.find('td', {'class': 'showAge'}).span.attrs['title']
		tx['out'] = tTx.find('td', {'class': 'text-center'}).text == 'OUT'
		tx['fee']['count'] = float( tTx.find('span', {'class': 'small text-secondary'}).text )

		txs.append(tx)

	return (txs)

def get_all_txs_wallet_polygon(address: str, txs_count: int):
	walletTxs = [] # tx is {'from':'0x000', 'to':'', 'fee':{'wei':1000, 'count': 1.0, 'in_usd': '0.13'}}
	
	if (txs_count == 0):
		return (walletTxs)

	pageIndex = 1
	while len(walletTxs) < txs_count:
		resp = get_res_page_txs(address, pageIndex)
		parsedTxs = get_wallet_txs_by_page(resp)
		walletTxs.extend( parsedTxs )
		pageIndex += 1

	return walletTxs

def get_acounts_by_wallets(file):
	with open(file) as f:
		wallets = f.readlines()

	accounts = []

	for wallet in wallets:
		wallet = wallet.strip().lower()
		acc = Account(wallet)

		firstRes = get_res_page_txs(wallet)
		soup = BeautifulSoup(firstRes.text)

		txsCount = int(soup.find_all('span', {'class': 'd-flex align-items-center'})[0].text.split(' ')[3].replace(',', '')) # magic move

		walletTxs = get_all_txs_wallet_polygon(wallet, txsCount)

		f_time = datetime.datetime.strptime(walletTxs[-1]['time'], "%Y-%m-%d %H:%M:%S")
		l_time = datetime.datetime.strptime(walletTxs[0]['time'], "%Y-%m-%d %H:%M:%S")
		acc.fist_trans[Chain.ChainName.POLYGON] = f_time.strftime("%d-%m-%Y %H:%M:%S")
		acc.last_trans[Chain.ChainName.POLYGON] = l_time.strftime("%d-%m-%Y %H:%M:%S")
		acc.fee_pay[Chain.ChainName.POLYGON] = dict()
		acc.fee_pay[Chain.ChainName.POLYGON]['count'] = sum(
			tx['fee']['count'] for tx in walletTxs
		)
		acc.trans_count[Chain.ChainName.POLYGON] = txsCount

		avgTimeDelta = (l_time - f_time) / txsCount
		hours, rem = divmod(avgTimeDelta.total_seconds(), 3600)
		mins, secs = divmod(rem, 60)
		acc.avg_time_trans[Chain.ChainName.POLYGON] = f"{int(hours)}:{int(mins)}:{int(secs)}"

		# print(acc)
		accounts.append(acc)

	return (accounts)

import aiohttp

from models import Chain
from utils.tokens import nfts_from_transactions

async def set_accounts_nfts(accounts, ERCcontracts):
    ret_ERCcontracts = {}
    bad_ERCcontracts = {}
    async with aiohttp.ClientSession() as session:
        # Other chians

        for chain_name in ERCcontracts:
            try:
                for ind, acc in enumerate(accounts):
                    if acc.wallet in ERCcontracts[chain_name]:
                        url = Chain.NFTsTransByAddrContract().get_by_chain_name(chain_name)
                        for addressContract in ERCcontracts[chain_name][acc.wallet]:
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
                                        token = await nfts_from_transactions(json_data['result'], acc.wallet)
                                        if chain_name not in accounts[ind].nfts:
                                            accounts[ind].nfts[chain_name] = {
                                            }
                                        accounts[ind].nfts[chain_name].update(
                                            token)
                                except:
                                    if chain_name not in bad_ERCcontracts:
                                        bad_ERCcontracts[chain_name] = {}
                                    if acc.wallet not in bad_ERCcontracts[chain_name]:
                                        bad_ERCcontracts[chain_name][acc.wallet] = [
                                        ]
                                    bad_ERCcontracts[chain_name][acc.wallet].append(
                                        addressContract)
                                    await asyncio.sleep(5)

            except Exception as e:
                print(f"Error in set_accounts_nfts {chain_name}\n{e}")
    return (accounts, ret_ERCcontracts, bad_ERCcontracts)
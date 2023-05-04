import asyncio
import json

async def shit(i):
	if i % 2 == 0:
		return 'ok'
	return 'no'

async def main():
	for i, val in enumerate(wallets):
		wallets[i] = await shit(i)
	print(json.dumps(wallets, indent=4))

if __name__ == "__main__":
	wallets = {}
	for i in range(10):
		wallets[i] = 'no'

	asyncio.run(main())

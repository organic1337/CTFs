
import re
from pwn import *


COIN_WEIGHT = 10
OUTPUT_PATTERN = re.compile(r'N=(?P<coins>\d*) C=(?P<chances>\d*).*')


def search_counterfeit(connection: remote, start: int, end: int) -> int:
	print(f'start={start}, end={end}')
	start_end_delta = end - start

	if start == end - 1:
		return start

	search_end = end - start_end_delta // 2
	searched_coins = ' '.join(str(coin_index) for coin_index in range(start, search_end))
	print(f'searched coins: {start} ... {search_end}')

	connection.writeline(searched_coins.encode())
	total_weight = int(connection.read().decode().strip())
	print(f'total_weigth={total_weight}')

	if total_weight % COIN_WEIGHT == 0:
		return search_counterfeit(connection, start + start_end_delta // 2, end)
	else:
		return search_counterfeit(connection, start, end - start_end_delta // 2)




connection = remote('pwnable.kr', 9007)
connection.read()

for i in range(100):
	output = connection.readuntil('\n').decode().strip()
	print(f'{i + 1}) {output}')
	coins_count = int(OUTPUT_PATTERN.match(output).group('coins'))	

	counterfeit_coin = search_counterfeit(connection, 0, coins_count)
	connection.writeline(str(counterfeit_coin).encode())
	connection.readuntil('\n')


print(connection.read())

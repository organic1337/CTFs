"""
Solution for slow network :(

Connect with ssh to one of the challanges and run it from there.

(run with python3)
"""
import re
import socket


COIN_WEIGHT = 10
OUTPUT_PATTERN = re.compile(r'N=(?P<coins>\d*) C=(?P<chances>\d*).*')
BUFFER = 4096

def search_counterfeit(connection, start, end):
	start_end_delta = end - start

	if start == end - 1:
		return start

	search_end = end - start_end_delta // 2
	searched_coins = ' '.join(str(coin_index) for coin_index in range(start, search_end))

	connection.send(searched_coins.encode() + b'\n')
	total_weight = int(connection.recv(BUFFER).decode().strip())

	if total_weight % COIN_WEIGHT == 0:
		return search_counterfeit(connection, start + start_end_delta // 2, end)
	else:
		return search_counterfeit(connection, start, end - start_end_delta // 2)




connection = socket.socket()
connection.connect(('pwnable.kr', 9007))
connection.recv(BUFFER)

for i in range(100):
	output = connection.recv(BUFFER).decode().strip()
	print('{}) {}'.format(i + 1, output))
	coins_count = int(OUTPUT_PATTERN.match(output).group('coins'))	

	counterfeit_coin = search_counterfeit(connection, 0, coins_count)
	print(counterfeit_coin)
	connection.send(str(counterfeit_coin).encode() + b'\n')
	connection.recv(BUFFER)


print(connection.recv(BUFFER).decode())

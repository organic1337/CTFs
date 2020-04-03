# Solution
The solution for this is using the Format string bug exploit 
to read data from the stack. Just provide a string of 
many '%x', find ascii sequences that ends with a nullbyte, 
translate it from little endian to big endian, convert to ASCII
and this is the password.

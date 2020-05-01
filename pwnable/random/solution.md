# Solution for `random`
The generated random number is always 0x6b8b4567 since the PRF seed 
is not explicitly changed. So xoring the 'random' value with deadbeef will give us 
the wanted input

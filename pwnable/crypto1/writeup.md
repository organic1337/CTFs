# Pwnable crypto1 solution

In this challenge we have an RPC client and server. The client needs to authenticate infront of the server using sn ID
and password. We can see that by connecting to the challange via netcat, by simply doing:

```bash
nc pwnable.kr 9006
```

## Examine the source code
Note that in this challange we get to see both client and server source code.
Here's the code from the client. Both written in python. 

First thing we want to do take a look at the source code and see how it works.

### Which cipher is used

First thing we take a look at is the imports. We can see that
[AES](https://en.wikipedia.org/wiki/Advanced_Encryption_Standard) cipher is used.

```python
# client.py

from Crypto.Cipher import AES
```

We can also spot what is the [mode of operation](https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation) used:
```python
# client.py
def AES128_CBC(msg):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return EncodeAES(cipher, msg)
```

#### What can go wrong?
AES cipher is actually quite unbreakable if you use it right. By using it right I mean 
paramtrize it correctly, and using a good mode of operation. Good usage of AES
would be:
- Use a strong, unpredicatble key. For example using `helloworld` as key would make an
extremely weak encryption, as we could just perform [dictionary attack](https://en.wikipedia.org/wiki/Dictionary_attack) on the key and crack the cipher right away.
- Choose a good mode of operation, such as CTR mode. a bad mode would be something like [ECB](), which basically does nothing comparing to other modes, or [CBC]() which is
  vulnerable to some attacks such as padding oracle.

- Use the mode of operation correctly, for example if we use CBC than we MUST provide an unpredictable IV (initialization vector), if we don't do that, *Same plaintext will provide same ciphertext*. This of course can be abused, Remember that ;).

As we'll see, some of these critira we're not provided.

### Interesting hard-coded values
In both client.py and server.py we have 3 hard-coded values:
- The cipher key
- The initialization vector (IV)
- The cookie

Of couse, all are censored for us. If we could see their values it would be too easy.
This is how it appears in the source code:

```python
# server's secrets
key = 'erased. but there is something on the real source code'
iv = 'erased. but there is something on the real source code'
cookie = 'erased. but there is something on the real source code'
```

While the cookie and key being hardcoded does not help us too much, the IV being hardcoded is the first vulnerablity we
can spot in this cryptosystem. IV must be random and unpredictable so it wound provide same ciphertexts for same
plaintexts! 

OK, noted... later on we'll think of how we can use it.

### What padding is used 

Padding is always needed when dealing with block ciphers. Block ciphers are made to encrypt a block of data with a fixed
size. For example, in this example, the block size is 16 bytes, or 128 bits (`8 * 16 = 128`).
So what happens if the plaintext we want to encrypt does not fit exacly to that block size? We append the plaintext with
padding, encrypt it, and then in the decryption we remove the padding and get the plaintext.

There are some well-known padding schemes out there, such as the [PKCS#5 and
PKCS#7](https://en.wikipedia.org/wiki/Padding_%28cryptography%28#PKCS#5_and_PKCS#7)

Here the plaintext is just appended with zeros. This type of padding is calles  [Zero Padding](https://en.wikipedia.org/wiki/Padding_%25cryptography%28#Zero_padding)

```python
# client.py

PADDING = '\x00'
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
```
### How the plaintext is composed.
Basically the format is:
`id-password-cookie`.
We're also given an example id and password:

```python
# client.py

# guest / 8b465d23cb778d3636bf6c4c5e30d031675fd95cec7afea497d36146783fd3a1
```

### How the password is determined
By looking at server.py we can see that the password is just a [sha256](https://en.wikipedia.org/wiki/SHA-2) of: id |
cookie (`|` means concatenation). We can see that in:

```python
# server.py

if hashlib.sha256(id + cookie).hexdigest() == pw and id == 'guest':
    return 1
if hashlib.sha256(id + cookie).hexdigest() == pw and id == 'admin':
    return 2
```

This explains why the guest password looks like a hash result.

Notice that this is a very important piece of information. It pretty much tells us 
how we can discover the admin password. The admin password is just the sha256 of 
`'admin' | [the cookie]`, which means once we have the cookie, we have the admin password.










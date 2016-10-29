import binascii
import datetime
import Crypto
from Crypto.PublicKey import RSA
from Crypto import Random
import ast

print("--Verifying certificate--")
filename = input("Type cert filename to verify")
f = open(filename + ".cert", 'r')
message = f.read()
message = message.split('\n')

privkey = message[len(message)-3].strip('\t')
md5rsa = message[len(message)-1]

privkey = privkey[2:len(privkey)-1]
md5rsa = md5rsa[2:len(md5rsa)-1]
# print(privkey)
# print(md5rsa)

privkeyBytes = binascii.unhexlify(privkey)
md5rsaBytes = binascii.unhexlify(md5rsa)
# print(privkeyBytes)
# print(md5rsaBytes)

key = RSA.importKey(privkeyBytes)
decryptedMD5 = key.decrypt(md5rsaBytes)

import hashlib
message = message[0:len(message)-2]
message = "\n".join(s for s in message)
message = message.encode('utf-8')
md5hash = hashlib.md5(message).digest()

# print(md5hash)
# print(decryptedMD5)
if md5hash == decryptedMD5:
    print("Certificate is valid!")
else:
    print("Certificate is unvalid!")

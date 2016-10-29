import datetime
import Crypto
from Crypto.PublicKey import RSA
from Crypto import Random
import ast
import binascii


def binaryToHexstring(keyBytes):
    byteVar = binascii.hexlify(keyBytes)
    return str(byteVar)
    # return "".join("%02x" % b for b in byteVar)


def getRSAKeys():
    random_generator = Random.new().read
    privateKey = RSA.generate(4096, random_generator) #generate pub and priv key
    publicKey = privateKey.publickey() # pub key export for exchange
    return (binaryToHexstring(publicKey.exportKey('DER')),
            binaryToHexstring(privateKey.exportKey('DER')),
            publicKey, privateKey)


print("---Certiface generator---")
filename = input("Please type certificate filename")
name = input("Please give your name")
surname = input("Please give your surname")
mail = input("Please give your mail")
country = input("Please give your country")
group = input("Please give your group name")
todayDate = datetime.datetime.now()
expireDate = todayDate + datetime.timedelta(days=5)
# print(todayDate)
# print(expireDate)

print("Wait... generating RSA keys")
exportedPublicKey, exportedPrivateKey, pubKey, privKey = getRSAKeys()
# print(exportedPublicKey)
# print(exportedPrivateKey)
# print(pubKey)
# print(privKey)

certificateData = "--Certificate--"
certificateData += "\n\tName: " + name
certificateData += "\n\tSurname: " + surname
certificateData += "\n\tMail: " + mail
certificateData += "\n\tCountry: " + country
certificateData += "\n\tGroup: " + group
certificateData += "\n\tDateCreated: " + str(todayDate)
certificateData += "\n\tDateExpire: " + str(expireDate)
certificateData += "\n\t\tPublic key:\n"
certificateData += "\t\t\t" + exportedPrivateKey

bytesCertificateData = certificateData.encode('utf-8')

import hashlib
md5hash = hashlib.md5(bytesCertificateData).digest()
encrypted = pubKey.encrypt(md5hash, 32)
encryptedHexstr = binaryToHexstring(encrypted[0])
# print(encryptedHexstr)
# print(exportedPublicKey)

certificateData += "\n--Md5Rsa--\n"
certificateData += encryptedHexstr

f = open (filename + '.cert', 'w')
f.write(str(certificateData))
f.close()

print("Certificate generated! File: " + filename + ".cert")

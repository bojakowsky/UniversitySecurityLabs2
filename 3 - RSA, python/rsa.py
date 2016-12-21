import gmpy2
from Crypto.Util.number import long_to_bytes, bytes_to_long
import random
import math
import timeit
from bitstring import BitArray
import hashlib

"""
Other stuff (https://en.wikipedia.org/wiki/Euclidean_algorithm):
Bezout's identity, Extended Euclidean algorithm, Matrix method, Euclid's lemma and unique factorization,
Linear Diophantine equations, Multiplicative inverses and the RSA algorithm,
Chinese remainder theorem, Stern-Brocot tree, Continued fractions
"""

"""numbers satisfying the equation: (a ** (n-1)) mod n == 1"""
CARMICHAEL_NUMBERS = [561, 41041, 825265, 321197185, 5394826801, 232250619601, 9746347772161]


def generate_carmichael_numbers(n):
    """
    Returns list of carmichael numbers from 1 to n
    :param n: upper border to look for carmichael numbers
    """
    carmichael_numbers_list = []

    # composite numbers
    # composites = [x for x in sieve(n) if x is False]
    sieve_arr = sieve(n)

    #Enumerate through numbers from 1 to n
    for number in xrange(1, n, 2):
        is_carmichael = True
        # only composite numbers
        if sieve_arr[number]:
            continue

        # get list of coprimes to number
        list_of_coprimes = get_coprimes_range(number, 2, number - 1)
        # if no coprimes, continue
        if len(list_of_coprimes) == 0:
            continue

        # enumerate over coprimes
        for coprime in list_of_coprimes:
            #check if (coprime ** (number - 1)) mod number == 1
            if pow(coprime, number-1, number) != 1:
                # Break loop, not carmichael number
                is_carmichael = False
                break

        if is_carmichael:
            carmichael_numbers_list.append(number)
    return carmichael_numbers_list


def get_coprimes_range(n, beg, end):
    """
    Return list of coprimes to n from given range <beg, end>
    :param n: number to check coprimility against
    :param beg: begin of the range to check with
    :param end: end of the range to check with
    """
    coprime = []
    for i in range(beg, end + 1):
        if is_coprime(n, i):
            coprime.append(i)
    return coprime


def is_coprime(a, b):
    """
    Return if number a is coprime to b (relatively prime), that is - their gcd(a,b) = 1
    :param a: first number
    :param b: second number
    """
    if gcd(a, b) == 1:
        return True
    return False


def is_composite(n):
    """
    Return if number n is composite (non prime)
    :param n: number to check
    """
    if n == 2:
        return False

    if n % 2 != 0:
        f = factorize_fermat(n)
        if f[0] == 1:
            return False
    return True


def gcd(a, b):
    """
    return Greatest common divisor - classic euclidean algorithm
    :param a: first number
    :param b: second number
    """
    while a != b:
        if a > b:
            a = a - b
        else:
            b = b - a
    return a

def gcd_mod(a, b):
    """
    return Greatest Common Divisor - another classic euclidean algorithm
    :param a: first number
    :param b: second number
    """
    if b == 0:
        return a
    else:
        return gcd(b, a % b)


def gcd_bin(u, v):
    """
    https://en.wikipedia.org/wiki/Binary_GCD_algorithm
    C recursive rewritten
    """
    # simple cases (termination)
    if u == v:
        return u

    if u == 0:
        return v

    if v == 0:
        return u

    # look for factors of 2
    if ~u & 1: # u is even
        if v & 1: # v is odd
            return gcd(u >> 1, v)
        else: # both u and v are even
            return gcd(u >> 1, v >> 1) << 1

    if ~v & 1: # u is odd, v is even
        return gcd(u, v >> 1)

    # reduce larger argument
    if u > v:
        return gcd((u - v) >> 1, v)

    return gcd((v - u) >> 1, u)


def is_prime_naive(n):
    """
    Return if number is prime - classical naive algorithm
    :param n: number to be checked for primality
    """
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    for i in range(3, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True


def sieve(limit):
    """
    Returns a list of the prime numbers up to limit (from 0 to limit).
    """
    limit += 1 # from 0 to 16
    a = [True] * limit
    a[0] = a[1] = False

    for i in range(2, int(math.sqrt(limit))):
        if a[i]:
            for c in range(i*i, limit, i):
                a[c] = False
    return a


def sieve_gmpy2_iter(limit):
    """
    Returns a list of the prime numbers up to limit (from 0 to limit).
    A bit faster
    https://gmpy2.readthedocs.io/en/latest/advmpz.html
    """
    # Increment by 1 to account for the fact that slices  do not include
    # the last index value but we do want to include the last value for
    # calculating a list of primes.
    sieve_limit = gmpy2.isqrt(limit) + 1
    limit += 1

    # Mark bit positions 0 and 1 as not prime.
    bitmap = gmpy2.xmpz(3)

    # Process 2 separately. This allows us to use p+p for the step size
    # when sieving the remaining primes.
    bitmap[4 : limit : 2] = -1

    # Sieve the remaining primes.
    for p in bitmap.iter_clear(3, sieve_limit):
        bitmap[p*p : limit : p+p] = -1

    return bitmap.iter_clear(2, limit)
    #return list(bitmap.iter_bits())


def factorize_fermat(n):
    """
    Returns pair of factors - odd numbers only
    :param n: number to be factorized
    """
    assert n % 2 != 0 # odd numbers only

    a = math.ceil(math.sqrt(n))
    b2 = a * a - n
    while not is_square(b2):
        a += 1
        b2 = a * a - n

    b = math.sqrt(b2)
    return int(a - b), int(a + b)


def is_square(n):
    """
    Return if n number is square
    :param n: number
    """
    # return math.sqrt(n) % 1 == 0
    return gmpy2.isqrt(n) % 1 == 0


def is_prime_fermat(n, k):
    """
    Return if number is probably prime - Fermat primality test
    :param n: number to be checked for primality
    :param k: number of times to perform check, greater number - more accurate algorithm is
    """
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False

    for _ in xrange(k):
        rand_number = random.randint(1, n - 1)
        if pow(rand_number, n - 1, n) != 1:
            return False
    return True


def is_prime_miller_rabin(n, k):
    """
    source: https://rosettacode.org/wiki/Miller%E2%80%93Rabin_primality_test#Python:_Probably_correct_answers
    Miller-Rabin primality test. Returns True if probably prime
    :param n: number to be checked for primality
    :param k: number of times to perform check, greater number - higher probability of being correct
    """
    #0, 1 - not prime
    if n < 2:
        return False
    #2 - prime, 4, 6 (evens) - not prime
    if n % 2 == 0:
        return n == 2

    # write n-1 as 2**s * d
    # repeatedly try to divide n-1 by 2
    s = 0
    d = n - 1
    while True:
        quotient, remainder = divmod(d, 2)
        if remainder == 1:
            break
        s += 1
        d = quotient
    assert (2 ** s * d == n - 1)

    # test the base a to see whether it is a witness for the compositeness of n
    def try_composite(a):
        if pow(a, d, n) == 1:
            return False
        for i in range(s):
            if pow(a, 2 ** i * d, n) == n - 1:
                return False
        return True  # n is definitely composite

    for i in range(k):
        a = random.randrange(2, n)
        if try_composite(a):
            return False

    return True  # no base tested showed n as composite


def bits_in_number(number):
    """
    Returns number of bits in the given number
    :param number: long number
    """
    if number == 0:
        return 0
    return gmpy2.mpz(gmpy2.floor(gmpy2.log2(number)) + 1)


def max_bits_in_digits(d):
    """
    Returns maximum number of bits fitting in given number of digits eg. 2 digits (99) fits in 7 bits
    :param d: number of digits
    """
    return gmpy2.mpz(gmpy2.ceil(d * (gmpy2.log(10) / gmpy2.log(2))))


def rand_n_bits_number(n, even = False):
    """
    Returning random number with n bits
    :param n: number of bits to be randed
    :param even: should generated number be even (default False) or odd (default True)
    """
    bit_array = BitArray(n)
    bit_array.set(True, 0)
    for i in xrange(1, n):
        bit = random.randint(0, 1)
        bit_array.set(bit, i)
    if not even:
        bit_array.set(True, n - 1)
    return bit_array.uint
    # return len(str(bit_array.uint)), bit_array.uint, bit_array.bin


def multiplicative_inverse(e, phi):
    """
    https://gist.github.com/JonCooperWorks/5314103
    Extended Euclidean - for test purposes
    """
    d = 0
    x1 = 0
    x2 = 1
    y1 = 1
    temp_phi = phi

    while e > 0:
        temp1 = temp_phi / e
        temp2 = temp_phi - temp1 * e
        temp_phi = e
        e = temp2

        x = x2 - temp1 * x1
        y = d - temp1 * y1

        x2 = x1
        x1 = x
        d = y1
        y1 = y

    if temp_phi == 1:
        return d + phi


class RSA:
    """
    Class for computing RSA public_key, private_key, signing text, and veryfing text
    """
    def __init__(self):
        self.private_key = 0
        self.public_key = 0

    def generate(self, bits, k=999):
        """
        Return public and private key of RSA
        :param bits: minimum number of bits for p and q
        :param k: number of checks in miller_rabin algorithm
        """
        p = q = 0
        while True:
            p = rand_n_bits_number(bits)
            if is_prime_miller_rabin(p, k):
                break

        # every 24 bits, about 7 digits difference - rand between 14 and 42 digits difference
        pq_bits_difference = random.randint(48, 144)
        while True:
            q = rand_n_bits_number(bits + pq_bits_difference)
            if is_prime_miller_rabin(q, k):
                break
        n = gmpy2.mpz(p) * gmpy2.mpz(q)
        phi_n = gmpy2.mpz(p-1) * gmpy2.mpz(q-1)

        e = 0
        temp = rand_n_bits_number(16, even=True)
        while True:
            if gmpy2.gcd(temp, phi_n) == 1:
                e = gmpy2.mpz(temp)
                break
            temp += 1
        assert e < phi_n

        # ext = multiplicative_inverse(e, phi_n)
        ext = gmpy2.gcdext(e, phi_n)
        if ext[0] == 1:
            d = phi_n + ext[1]
        assert (d * e % phi_n == 1)

        self.private_key = (d, n)
        self.public_key = (e, n)

        return self.public_key, self.private_key

    def encrypt(self, text):
        cipher = ""
        for t in text:
            cipher += str(gmpy2.powmod(ord(t), self.public_key[0], self.public_key[1])) + " "
        return cipher

    def decrypt(self, cipher):
        text = ""
        cipher = cipher.split(" ")
        for c in cipher:
            if len(c) != 0:
                text += chr(gmpy2.powmod(gmpy2.mpz(c), self.private_key[0], self.private_key[1]))
        return text

    def sign(self, text):
        sign = ""
        text = hashlib.sha512(text).hexdigest()
        for t in text:
            sign += str(gmpy2.powmod(ord(t), self.private_key[0], self.private_key[1])) + " "
        return sign

    def verify_sign(self, sign, text_original):
        text = ""
        sign = sign.split(" ")
        try:
            for s in sign:
                if len(s) != 0:
                    text += chr(gmpy2.powmod(gmpy2.mpz(s), self.public_key[0], self.public_key[1]))
        except:
            return False
        return text == hashlib.sha512(text_original).hexdigest()


# num = 99999
# print gcd(32,  64)
# print gcd_bin(32,  64)
# print is_prime_fermat(num, 555)
# print is_square(num)
# print is_prime_naive(num)
# print generate_carmichael_numbers(num)
# print factorize_fermat(10403)
# print sieve(num)
# print list(sieve_gmpy2_iter(num))
# print is_prime_miller_rabin(93601, 500)
# print is_composite(16)
# print is_coprime(16, 8)

# print bits_in_number(0)
# print bits_in_number(1)
# print bits_in_number(16)
# print bits_in_number(33)
# print max_bits_in_digits(2)
# print rand_n_bits_number(1048)
# print is_square(16)
# x = gmpy2.mpz(797572970182509660703132216930939914570255851132318319795831043113690942780895298 \
# 5652312752258825399861695026257855229956923650800305607896087864451283099)
# print is_prime_miller_rabin(x, 9999)

text = '''
RSA is one of the first practical public-key cryptosystems and is widely used for secure data transmission. In such a
cryptosystem, the encryption key is public and differs from the decryption key which is kept secret. In RSA, this
asymmetry is based on the practical difficulty of factoring the product of two large prime numbers, the
factoring problem. RSA is made of the initial letters of the surnames of Ron Rivest, Adi Shamir, and Leonard Adleman,
who first publicly described the algorithm in 1977. Clifford Cocks, an English mathematician working for the UK
intelligence agency GCHQ, had developed an equivalent system in 1973, but it was not declassified until 1997.[1]
A user of RSA creates and then publishes a public key based on two large prime numbers, along with an auxiliary
value. The prime numbers must be kept secret. Anyone can use the public key to encrypt a message, but with currently
published methods, if the public key is large enough, only someone with knowledge of the prime numbers can feasibly
decode the message.[2] Breaking RSA encryption is known as the RSA problem; whether it is as hard as the factoring
problem remains an open question. RSA is a relatively slow algorithm, and because of this it is less commonly
used to directly encrypt user data. More often, RSA passes encrypted shared keys for symmetric key cryptography
which in turn can perform bulk encryption-decryption operations at much higher speed.
'''

start = timeit.default_timer()

rsa = RSA()

#generate rsa keys
print rsa.generate(1024, 999)

#encrypt text
cipher = rsa.encrypt(text)
print cipher

#decrypt encrypted text
decrypt = rsa.decrypt(cipher)
print decrypt

#sign text
signed = rsa.sign(text)
print signed

#verify sign
print rsa.verify_sign(signed, text)
signed = "86" + signed[2:]
print rsa.verify_sign(signed, text)

stop = timeit.default_timer()
print stop - start
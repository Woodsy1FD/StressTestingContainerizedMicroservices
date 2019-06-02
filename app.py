import time

import redis
from flask import Flask
from flask.json import jsonify

from math import sqrt


app = Flask(__name__)
cache = redis.Redis(host='redis', port=6379,decode_responses=True) # decode responses so its not aids


def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)


# Determines if n is a prime number
# Returns: boolean TTrue or False
def is_prime(n):
    # 2 is obv prime
    if n == 2:
        # Store value in redis key 'primes'
        #cache.append("primes", str(n)+ ",")
        cache.rpush("primeList", n) # add to list
        return True
    # if dividing by 2 = 0 or less than or equal to 1 => not prime
    if n % 2 == 0 or n <= 1:
        return False

    # Find sqrt and then add 1 (only need to check up to sqrt of number)
    sqr = int(sqrt(n)) + 1

    # check all values between 3 and sqr, in intervals of 2
    # this is efficient in terms of memory as range always uses the same small amount of memory
    # as it only stores start, stop, step values
    # https://docs.python.org/3/library/stdtypes.html#typesseq-range
    for div in range(3, sqr, 2):
        if n % div == 0: # if divisible by a divisor in range, not prime
            return False
    # Store value in redis list 'primeList'
    cache.rpush("primeList", n)
    return True

# Get list of primes from redis
def get_primes_redis():
    listPrime = cache.lrange("primeList", 0, -1)
    return listPrime
    

# Basic route
@app.route('/')
def hello():
    count = get_hit_count()
    return 'Hello World! I have been seen {} times.\n'.format(count)


# Route for Requirement 1
# int:number uses a converter to specify the type
@app.route('/isPrime/<int:number>')
def isPrime(number):
    res = is_prime(number)
    if(res):
        return '{} is prime\n'.format(number)
    return '{} is not prime\n'.format(number)


# Route for Requirement 2
@app.route('/primesStored')
def primesStored():
    listPrimes = get_primes_redis()
    return jsonify({'primes': listPrimes})
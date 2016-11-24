'''
Created on Nov 24, 2016

@author: tim
'''
import redis
import bcrypt
import json

unis = redis.Redis('localhost', db = 0)
tags = redis.Redis('localhost', db = 1)
users = redis.Redis('localhost', db = 2)
cards = redis.Redis('localhost', db = 3)
schedules = redis.Redis('localhost', db = 4)
stats = redis.Redis('localhost', db = 5)
tags = redis.Redis('localhost', db = 6)
variables = redis.Redis('localhost', db = 7)

for key in cards.scan_iter():
    print key, cards[key]

for key in stats.scan_iter():
    print key, stats[key]

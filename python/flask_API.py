'''
Created on Nov 24, 2016

@author: tim
'''
from flask import Flask
from flask.ext.cors import CORS
from flask import request
from crossdomain import crossdomain
import numpy as np
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

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

def join_name(*names):
    key = ''
    for name in names:
        key +=str(name) + '.'
    return key[:-1]

def verify_user(user, pw):
    if not users.exists(user): return False
    if users.get(user) == bcrypt.hashpw(pw.encode('utf-8'), users.get(user)): return True
    else: return False

@app.route('/adduser', methods=['OPTIONS', 'GET', 'POST'])
@crossdomain(origin='*')
def add_user():
    user = request.values.get('user')
    pw = request.values.get('password')

    if users.exists(user): return json.dumps(False)
    hashed = bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt())
    users.set(user, hashed)
    return json.dumps(True)

@app.route('/login', methods=['OPTIONS', 'GET', 'POST'])
@crossdomain(origin='*')
def login():
    user = request.values.get('user')
    pw = request.values.get('password')

    success = verify_user(user, pw)
    return json.dumps(success)

@app.route('/addcard', methods=['OPTIONS', 'GET', 'POST'])
@crossdomain(origin='*')
def addcard():
    Q = request.values.get('question')
    A = request.values.get('answer')
    card_tags = json.loads(request.values.get('tags'))
    uni = request.values.get('uni')

    if not unis.exists(uni): unis.sadd(uni, *card_tags)

    variables.incr('cardid')
    cardid = variables.get('cardid')

    for tag in card_tags:
        if not tags.exists(tag): tags.sadd(tag, cardid)

    cards.set(cardid, {'q' : Q, 'a' : A, 'tags' : card_tags, 'uni' : uni})

    return json.dumps(True)

@app.route('/sendresult', methods=['OPTIONS', 'GET', 'POST'])
@crossdomain(origin='*')
def sendresult():
    user = request.values.get('user')
    cardid = request.values.get('cardid')
    result = request.values.get('result')

    key = join_name(user,cardid)
    if not stats.exists(key): stats.set(key,json.dumps({ "n" : 0, "seq" : []}))

    stat = json.loads(stats.get(key))
    if result > 1: stat['n'] += 1
    stat['seq'].append(result)
    stats.set(key, json.dumps(stat))

    return json.dumps(True)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000,threaded=True, debug=True, use_reloader=True)
    #app.run(host='0.0.0.0', port=5000,threaded=True, use_reloader=False)
    #app.run(host='127.0.0.1', port=5000,threaded=True, use_reloader=False)

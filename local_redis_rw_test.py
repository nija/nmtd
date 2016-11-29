#!/usr/bin/env python
"""
Client which receives the requests

Args:
    API Token
    API Base (https://...)

"""
from flask import Flask, request
import logging
import argparse
import urllib2
import redis

logging.basicConfig(level=logging.DEBUG)

# parsing arguments
PARSER = argparse.ArgumentParser(description='Client message processor')
PARSER.add_argument('API_token', help="the individual API token given to your team")
PARSER.add_argument('API_base', help="the base URL for the game API")

# ARGS = PARSER.parse_args()

# # defining global vars
# # MESSAGES = {} # A dictionary that contains message parts
# API_BASE = ARGS.API_base
# # 'https://csm45mnow5.execute-api.us-west-2.amazonaws.com/dev'

# Persistent connection to redis
redpool = redis.ConnectionPool(host='redis-msg.cdje8j.ng.0001.euc1.cache.amazonaws.com', port=6379, db=0)
testpool = redis.ConnectionPool(host='localhost', port=6379, db=0)

APP = Flask(__name__)


@APP.route('/test', methods=['GET'])
def test_rw():
    reddy = redis.Redis(connection_pool=testpool)
    path = '/parts/{}'.format('test')
    msg = "Got GET for test"
    print msg
    length = reddy.lpush(path, 'testvalue0')
    msg = "Pushed to redis 0 - testvalue0, length is {}".format(length)
    print msg
    length = reddy.lpush(path, 'testvalue1')
    msg = "Pushed to redis 1 - testvalue1, length is {}".format(length)
    print msg
    keys = reddy.keys('{}/*'.format(path))
    msg = "Pulled from redis"
    print msg
    return "There are {} messages in redis with keys {}".format(length, keys)


# creating flask route for type argument
@APP.route('/', methods=['GET', 'POST'])
def main_handler():
    """
    main routing for requests
    """
    if request.method == 'POST':
        # return process_message(request.get_json())
        send_to_redis(request.get_json())
    else:
        # return get_message_stats()
        return get_redis_stats()


def get_redis_stats():
    reddy = redis.Redis(connection_pool=redpool)
    redkeys = reddy.keys('/parts/*')
    return "There are {} messages in redis".format(len(redkeys))


def send_to_redis(msg):
    redpath = '/parts/{}'.format(msg['Id'])
    greenpath = '/complete'
    reddy = redis.Redis(connection_pool=redpool)
    length = reddy.lpush(redpath, msg)
    if length == msg['TotalParts']:
        length = reddy.lpush(greenpath, redpath)
    return True

if __name__ == "__main__":

    # By default, we disable threading for "debugging" purposes.
    # This will cause the app to block requests, which means that you miss out on some points,
    # and fail ALB healthchecks, but whatever I know I'm getting fired on Friday.
    APP.run(host="0.0.0.0")
    # APP.run(host="0.0.0.0", port="80")

    # Use this to enable threading:
    # APP.run(host="0.0.0.0", port="80", threaded=True)

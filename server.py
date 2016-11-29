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
import json

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

# parsing arguments
PARSER = argparse.ArgumentParser(description='Client message processor')
PARSER.add_argument('API_token', help="the individual API token given to your team")
PARSER.add_argument('API_base', help="the base URL for the game API")

ARGS = PARSER.parse_args()

# defining global vars
# MESSAGES = {} # A dictionary that contains message parts
API_BASE = ARGS.API_base
# 'https://csm45mnow5.execute-api.us-west-2.amazonaws.com/dev'

# Persistent connection to redis
redpool = redis.ConnectionPool(host='redis-msg.cdje8j.ng.0001.euc1.cache.amazonaws.com', port=6379, db=0)

APP = Flask(__name__)


# creating flask route for type argument
@APP.route('/', methods=['GET', 'POST'])
def main_handler():
    """
    main routing for requests
    """
    try:
        if request.method == 'POST':
            # return process_message(request.get_json())
            logger.debug('Got POST from {}'.format(request.get_json()))
            send_to_redis(request.get_json())
        else:
            # return get_message_stats()
            logger.debug('Got GET')
            return get_redis_stats()
    except ValueError as e:
        pass


def get_redis_stats():
    reddy = redis.Redis(connection_pool=redpool)
    redkeys = reddy.keys('/parts/*')
    return "There are {} messages in redis".format(len(redkeys))


def send_to_redis(msg):
    redpath = '/parts/{}'.format(msg['Id'])
    greenpath = '/complete'
    reddy = redis.Redis(connection_pool=redpool)
    length = reddy.lpush(redpath, json.dumps(msg))
    logger.debug('Pushed to redis({} {}): {}'.format(length, redpath, json.dumps(msg)))
    if length == int(msg['TotalParts']):
        length = reddy.lpush(greenpath, redpath)
        logger.debug('MSG COMPLETE: Pushed to redis({} {}): {}'.format(length, greenpath, redpath))
    return True

if __name__ == "__main__":

    # By default, we disable threading for "debugging" purposes.
    # This will cause the app to block requests, which means that you miss out on some points,
    # and fail ALB healthchecks, but whatever I know I'm getting fired on Friday.
    # APP.run(host="0.0.0.0", port="80")

    logger.debug("\n\t\tSTARTED SERVER - {}\n".format(ARGS))
    # Use this to enable threading:
    APP.run(host="0.0.0.0", port="80", threaded=True)
    logger.debug("\n\t\tSERVER STOPPED\n")

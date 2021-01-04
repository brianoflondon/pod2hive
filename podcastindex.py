# Functions to call the podcast index
# Thanks to CSB for the start.

import argparse
from datetime import date
import hashlib
import json
import requests
import time
import os


# setup some basic vars for the search api. 
# for more information, see https://api.podcastindex.org/developer_docs

import config

baseURL = 'https://api.podcastindex.org/'
apiCalls = {
    'byterm' : '/api/1.0/search/byterm?q=',
    'byfeed' : '/api/1.0/podcasts/byfeedurl?url=',
    'byfeedid' : '/api/1.0/podcasts/byfeedid?id=' ,
    'recentfeeds' : '/api/1.0/recent/feeds'
}

def getHeaders():
    """ Return the query headers """

    # the api follows the Amazon style authentication
    # see https://docs.aws.amazon.com/AmazonS3/latest/dev/S3_Authentication2.html
    # we'll need the unix time
    config.init()
    api_key = config.pod2api['key']
    api_secret = config.pod2api['secret']
    epoch_time = int(time.time())

    # our hash here is the api key + secret + time 
    data_to_hash = api_key + api_secret + str(epoch_time)
    # which is then sha-1'd
    sha_1 = hashlib.sha1(data_to_hash.encode()).hexdigest()

    # now we build our request headers
    headers = {
        'X-Auth-Date': str(epoch_time),
        'X-Auth-Key': api_key,
        'Authorization': sha_1,
        'User-Agent': 'postcasting-index-python-pod2hive'
    }
    return headers


def doCall(call, query):
    """ Takes in a call type see apiCalls above and returns the request or False """
    if call in apiCalls:
        url = baseURL + apiCalls[call] + query
        r = requests.post(url, headers=getHeaders())
        return r
    else:
        return False
    
    
def doRecent(max = 40, since = '', lang = '', cat = '', nocat = ''):
    query = f'?max={max}&cat={cat}&lang={lang}'
    return doCall('recentfeeds',query)


if __name__ == "__main__":
    pass

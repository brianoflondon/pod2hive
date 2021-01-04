# Minimal code needed to pull an RSS feed out of Hive

from beem import Hive
from beem.account import Account
import base64
import zlib
import json

import argparse

def txtDecomp(txt):
    """ Decompress text 
        Returns plain text """
    out = base64.b64decode(txt)
    out = zlib.decompress(out).decode()
    return out

# create and parse our args
parser = argparse.ArgumentParser()
parser.add_argument('--hive', dest='HiveAccount', type=str,
                    help="Hive account to fetch RSS from")
parser.set_defaults(HiveAccount='learn-to-code')
args = parser.parse_args()


""" Gets the RSS from a Hive account if it is in metadata """
h = Hive()
auth = args.HiveAccount
acc = Account(auth,blockchain_instance=h)
mData = json.loads(acc['posting_json_metadata'])

if 'podcastindex' in mData:
    if 'pod-rss' in mData['podcastindex']:
        rssComp = mData['podcastindex']['pod-rss']
        rss = txtDecomp(rssComp)
        print(rss)
else:
    print('No Data')
# Access the bits of the Hive blockchain we'll need
# Needs beempy running and storing the keys and set with
# Enviornment UNLOCK 

from beem import Hive
from beem.account import Account

import json
import requests
import zlib
import base64

import podcastindex as pind

txRecord = 'txRecord.json'

h = Hive()

def txtComp(txt):
    """ Take in text, compress it and output base64 encoded string
        Returns compressed encoded text as string """
    out = txt.encode()
    out = zlib.compress(out,9)
    out = base64.b64encode(out)
    out = out.decode()
    return out

def txtDecomp(txt):
    """ Decompress text 
        Returns plain text """
    out = base64.b64decode(txt)
    out = zlib.decompress(out).decode()
    return out


def getRssFromWeb(address):
    """ Returns as both compressed string and original RSS from a feed link """
    r = requests.get(address)
    cRSS = r.text
    return txtComp(cRSS), cRSS


def getPostingJsonMeta(auth):
    """ Gets the posting_json_metadata from the Hive account auth
        Returns Json object """
    acc = Account(auth,blockchain_instance=h)
    return json.loads(acc['posting_json_metadata'])


def writePostingJsonMeta(data, auth, wipe=False):
    """ Takes in data and writes it to the Author posting_json_metadata
        Adds it to exsiting meta data unless wipe is True in which case
        repalces all existing data """
    eMeta = getPostingJsonMeta(auth)
    newMeta = {**eMeta, **data}
    acc = Account(auth,blockchain_instance=h)
    tx = acc.update_account_jsonmetadata(newMeta, account=auth)
    saveTXRecord(tx)
    

def saveTXRecord(tx):
    """ Saves a TX record """
    with open(txRecord, 'a') as f:
        json.dump(f,tx)
        


if __name__ == "__main__":
    feedURLs = ['https://www.brianoflondon.me/podcast2/brians-forest-talks-exp.xml',
                'http://feed.nashownotes.com/rss.xml',
                'https://feeds.simplecast.com/gRpOClFR']
    feedURL = feedURLs[0]

    auth = 'learn-to-code'

    hiveJson = getPostingJsonMeta(auth)
    r = pind.doCall('byfeed',feedURL)
    rssComp, rss = getRssFromWeb(feedURL)
    
    feedInfoJson = r.json()
    
    with open('ltc-profile.json', 'r') as f:
        profiled = json.load(f)

    # writePostingJsonMeta(profiled,auth)
    
    # blank = {}
    # acc = Account(auth,blockchain_instance=h)
    # tx = acc.update_account_jsonmetadata(blank,account=auth)
    
    # tx =acc.update_account_metadata(blank,auth) # Account json metadata needs Active Key
    
    
    print('done')

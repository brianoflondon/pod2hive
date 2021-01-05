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


def getRSSFromHive(auth):
    """ Gets the RSS from a Hive account if it is in metadata 
        Returns 4 values, rss compressed rsss  """
    acc = Account(auth,blockchain_instance=h)
    mData = json.loads(acc['posting_json_metadata'])
    hasData = {}
    hasData['podcastindex'] = False
    hasData['pod-rss'] = False
    hasData['pod-rss-text'] = False
    mData['pod-rss-text'] = False
    
    if 'pod-rss' in mData:
        mData['pod-rss-text'] = txtDecomp(mData['pod-rss'])
        hasData['pod-rss'] = True
        hasData['pod-rss-text'] = True

    if 'podcastindex' in mData:
        hasData['podcastindex'] = True

    return mData,hasData
    

def writePostingJsonMeta(data, auth, wipe=False):
    """ Takes in data and writes it to the Author posting_json_metadata
        Adds it to exsiting meta data unless wipe is True in which case
        repalces all existing data """
    eMeta = getPostingJsonMeta(auth)
    newMeta = {**eMeta, **data}
    acc = Account(auth,blockchain_instance=h)
    tx = acc.update_account_jsonmetadata(newMeta, account=auth)
    saveTXRecord(tx)
    return tx
    

def saveTXRecord(tx):
    """ Saves a TX record """
    with open(txRecord, 'a') as f:
        json.dump(tx,f,indent=2)
        

def getPIinfoAndRss(url):
    """ Gets both the podcast index info and RSS feed for a URL
        Returns the dict and the raw rss text """
    r = pind.doCall('byfeed',url)
    rssComp, rss = getRssFromWeb(url)
    piInfo = {}
    piInfo['podcastindex'] = r.json()
    piInfo['pod-rss'] = rssComp
    return piInfo, rss


def getHiveNodes():
    """ Return a list of hive node URLS """
    from beem.nodelist import NodeList
    nodelist = NodeList()
    nodelist.update_nodes()
    nodes = nodelist.get_hive_nodes()
    return nodes

if __name__ == "__main__":
    feedURLs = ['https://www.brianoflondon.me/podcast2/brians-forest-talks-exp.xml',
                'http://feed.nashownotes.com/rss.xml',
                'https://feeds.simplecast.com/gRpOClFR']
    feedURL = feedURLs[0]

    auth = 'learn-to-code'
    auth = 'brianoflondon'
    
    nodes = getHiveNodes()

    piInfo, rss = getPIinfoAndRss(feedURL)
    
    mData,hasData = getRSSFromHive(auth)
    
    if hasData['pod-rss-text']:
        if mData['pod-rss-text'] == rss:
            # print(rssBack)
            print('podcast rss feed unchanged - We did it! The Same.')
    
    if hasData['podcastindex']:
        if mData['podcastindex'] == piInfo['podcastindex']:
            print('We did it! The Same.')
    
    mDataUpdate = False
    if mDataUpdate:
        tx = writePostingJsonMeta(piInfo,auth)


    
    # curl -s --data '{"jsonrpc":"2.0", "method":"database_api.find_accounts", "params": {"accounts":["learn-to-code"]}, "id":1}' https://api.hive.blog
    
    
    # with open('ltc-profile.json', 'r') as f:
    #     profiled = json.load(f)

    # writePostingJsonMeta(profiled,auth)
    
    # blank = {}
    # acc = Account(auth,blockchain_instance=h)
    # tx = acc.update_account_jsonmetadata(blank,account=auth)
    
    # tx =acc.update_account_metadata(blank,auth) # Account json metadata needs Active Key
    
    
    print('done')



hivenodes = ['https://api.deathwing.me', 
             'https://hived.emre.sh', 
             'https://hive.roelandp.nl', 
             'https://rpc.ausbit.dev', 
             'https://api.hive.blog', 'https://rpc.ecency.com', 'https://api.pharesim.me', 'https://api.openhive.network', 'https://hived.privex.io', 'https://hive-api.arcange.eu', 'https://api.c0ff33a.uk', 'https://api.hivekings.com', 'https://fin.hive.3speak.co', 'https://anyx.io', ...]
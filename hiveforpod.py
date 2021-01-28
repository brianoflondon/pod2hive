# Access the bits of the Hive blockchain we'll need
# Needs beempy running and storing the keys and set with
# Enviornment UNLOCK 

from beem import Hive
from beem.account import Account
from beem.comment import Comment
from beem.utils import construct_authorperm, sanitize_permlink
from beem.exceptions import ContentDoesNotExistsException
from beemapi.exceptions import UnnecessarySignatureDetected

import json
import requests
import zlib
import base64
import datetime
import time
import os.path


import podcastindex as pind
from mdutils import MdUtils

txRecord = 'txRecord.json'
run_as_acc = 'learn-to-code'

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
    acc = Account(run_as_acc,blockchain_instance=h)  
    try:
        tx = acc.update_account_jsonmetadata(newMeta, account=auth)
    except UnnecessarySignatureDetected:
        print('UnnecessarySignatureDetected')
        print('Something went wrong')
        tx = {}
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
    piInfo['pod-url'] = url
    return piInfo, rss


def getHiveNodes():
    """ Return a list of hive node URLS """
    from beem.nodelist import NodeList
    nodelist = NodeList()
    nodelist.update_nodes()
    nodes = nodelist.get_hive_nodes()
    return nodes

def getNodeSpeedTest(auth):
    """ Perform a speed test on all available nodes """
    import time

    nodes = getHiveNodes()
    speed = {}
    for node in nodes:
        start = time.perf_counter()
        h = Hive(node=node)
        acc = Account(auth,blockchain_instance=h)
        _ = json.loads(acc['posting_json_metadata'])
        end = time.perf_counter()
        elapse = end - start
        speed[node] = elapse
        # print(f'Node: {node} - Time: {elapse}')
    return speed

def checkExists(auth, pLink):
    """ Test if a pLink value has been posted by this author before 
        Returns True False.
        if True also returns the content body """
    authPLink = construct_authorperm(auth, pLink)
    try:
        c = Comment(authorperm=authPLink)
    except ContentDoesNotExistsException:
        return False, ''
    return True , c.body

def make_hive_perm_link(epi):
    """ Takes in a dictionar of episode information and contructs a permalink
        At first I used epi['id'] but this was unreliable, changed to using a
        hash of GUID instead 2021-01-24 
        Returns a string """
        
    # First check if this is an old episode we already did with the id.
    find_this = False
    if os.path.exists('old_episodes.json'):
        with open('old_episodes.json','r') as fl:
            old_episodes = json.load(fl)
        find_this = (next((item for item in old_episodes if item["title"] == epi['title']), False))
    # This line from: https://stackoverflow.com/a/31988734/9162717
    if find_this:
        p_link = find_this['permlink']
    else:       # Use the new version of hashing the GUID
        p_link = epi['title'] + '_' + str(hash(epi['guid']))
        p_link = sanitize_permlink(p_link)
    return p_link
    
    

def postEpisode(auth, url, id=None, postNew = True):
    """ Post an episode to the blochain if no id get latest """
    
    podInfo = pind.getPodInfoUrl(url).json()
    
    if id is None:
        episodes = pind.getEpisodes(url,1).json()
        # print(json.dumps(episodes,indent=2))
        if episodes['status']:
            for epi in episodes['items']:
                id = epi['id']
    else:
        episodes = pind.getEpisode(id).json()
        if episodes['status']:
            epi = episodes['episode']
        
            
    mf, _ = pind.episodeToMarkdown(epi, podInfo, auth)
            
    cBody = mf
    cTitle = epi['title']
    pLink = make_hive_perm_link(epi)
    
    # Only post if this is new content AND the body has changed.
    oldContent, bodyTxt = checkExists(auth,pLink)
    if postNew and (bodyTxt != cBody.file_data_text):
        tx = h.post(title = cTitle, 
                    body = cBody.file_data_text, 
                    author=auth,
                    tags=['podcast','pod2hive'],
                    permlink=pLink,
                    community='hive-136933') 
        saveTXRecord(tx)
    return oldContent


def postBackEpisodes(auth, feedURL, maX = None, postNew=True):
    epList = []
    if maX is not None:
        episodes = pind.getEpisodes(feedURL,maX).json()
    else:
        episodes = pind.getEpisodes(feedURL).json()
    if episodes['status']:
        for epi in episodes['items']:
            epList.append((epi['datePublished'],epi['id']))
    epList.sort(key = lambda x: x[0]) 
    print(epList)
    for epId in epList:
        print(pind.getEpisode(epId[1]).json()['episode']['title'])
        oldContent = postEpisode(auth,feedURL,epId[1],postNew)
        if postNew:
            if not oldContent:
                for n in range(5):
                    print(n)
                    time.sleep(60)
            else:
                time.sleep(6)
    
def scan_feeds_and_publish_once(feedURLs):
    new_episode = False
    while not new_episode:
        for auth in feedURLs:
            feedURL = feedURLs[auth]

            piInfo, rss = getPIinfoAndRss(feedURL)        
            mData,hasData = getRSSFromHive(auth)
            
            mDataUpdate = False
            if hasData['pod-rss-text']:
                if mData['pod-rss-text'] == rss:
                    # print(rssBack)
                    print(f'Feed unchanged: {auth} - {feedURL}')
                else:
                    print(f'Update needed:  {auth} - {feedURL}')
                    mDataUpdate = True
            else:
                print(f'Feed needs to be created: {auth} - {feedURL}')
                mDataUpdate = True
            
            # Podcastindex data will always changed because of access time
            # if hasData['podcastindex']:
            #     if mData['podcastindex'] == piInfo['podcastindex']:
            #         print('We did it! The Same.')
            #     else:
            #         print('Updating podcastindex data too')

            if mDataUpdate:
                tx = writePostingJsonMeta(piInfo,auth)
                postBackEpisodes(auth,feedURL,2,True)
                print(f'New episode')
                new_episode = True
        print('Sleeping ' + datetime.datetime.now().strftime('%c'))
        time.sleep(60*30)
        
    print('done')


def update_old_episodes(numBack, feedURLs):            
    # Update old episodes going back numbBack in a feed
    for auth in feedURLs:
        feedURL = feedURLs[auth]
        postBackEpisodes(auth,feedURL,numBack,False)
    

if __name__ == "__main__":
    feedURLs = {
        # 'brianoflondon' : 'https://www.brianoflondon.me/podcast2/brians-forest-talks-exp.xml',
        'no-agenda' : 'http://feed.nashownotes.com/rss.xml',
        'podcastindex' : 'https://mp3s.nashownotes.com/pc20rss.xml'
    }
    
    feed_community = {
        'no-agenda' : 'hive-136933',
        'podcastindext' : 'hive-136933'
    }
    scan_feeds_and_publish_once(feedURLs)
    # update_old_episodes(1,feedURLs)
    
   
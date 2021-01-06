# Functions to call the podcast index
# Thanks to CSB for the start.

import argparse
from datetime import date
import hashlib
import json
import requests
import time
import os
from mdutils import Html
from mdutils import MdUtils


# setup some basic vars for the search api. 
# for more information, see https://api.podcastindex.org/developer_docs

import config

baseURL = 'https://api.podcastindex.org/'
apiCalls = {
    'byterm' : '/api/1.0/search/byterm?q=',
    'byfeed' : '/api/1.0/podcasts/byfeedurl?url=',
    'byfeedid' : '/api/1.0/podcasts/byfeedid?id=' ,
    'recentfeeds' : '/api/1.0/recent/feeds',
    'epbyfeedurl' : '/api/1.0/episodes/byfeedurl?url=',
    'epbyfeedid' : '/api/1.0/episodes/byfeedid?id=',
    'epbyid' : '/api/1.0/episodes/byid?id='
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
    """ Get max recent podcasts """
    query = f'?max={max}&cat={cat}&lang={lang}'
    return doCall('recentfeeds',query)


def getEpisodes(feedURL, maX=None):
    """ Get max episodes from a feed """
    if maX is not None: 
        query = f'{feedURL}&max={maX}'
    else:
        query = f'{feedURL}'
    return doCall('epbyfeedurl', query)

def getEpisode(id):
    """ Get specific episode by episode id """
    query = f'{id}'
    return doCall('epbyid',query)



def episodeToMarkdown(data, auth):
    """ Take in a podcast episode data from PodcastIndex and return Markdowns """
    print(f'Working on {txt}')
    fileName = str(data['id']) +'.md'
    published = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime(data['datePublished']))
    mf = MdUtils(file_name=fileName,title=data['title'])
    txt = data['title'] + ' - ' + data['enclosureType']
    mf.new_line(mf.new_inline_link(link=data['enclosureUrl'],text=txt))
    mf.new_line(mf.new_inline_link(link=data['link'],text='Show Notes Link'))
    mf.new_line(f'Published: {published}')
    if 'image' in data:
        mf.new_paragraph(Html.image(path=data['image']))
    elif 'feedImage':
        mf.new_paragraph(Html.image(path=data['feedImage']))
    mf.new_paragraph(data['description'])
    mf.read_md_file('postfooter.md')
    mf.file_data_text = mf.file_data_text.replace('somethingtoreplacehere777',auth)
    print(f'Working on {txt}')
    return mf, fileName



if __name__ == "__main__":
    
    episodes = getEpisodes('http://feed.nashownotes.com/rss.xml').json()
    print(json.dumps(episodes,indent=5))
    auth = 'no-agenda'
    if episodes['status']:
        for epi in episodes['items']:
            print(epi['title'])
            # mf,_ =episodeToMarkdown(epi, auth)
            # print(mf.file_data_text)
    pass

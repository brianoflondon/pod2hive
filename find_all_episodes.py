from beem import Hive
from beem.account import Account
from beem.comment import Comment
from beem.exceptions import ContentDoesNotExistsException
from beem.utils import construct_authorperm, sanitize_permlink
from datetime import datetime
import os.path
import json

accs = {'podcastindex',
        'no-agenda',
        'brianoflondon'}


if os.path.exists('old_episodes.json'):
    with open('old_episodes.json','r') as fl:
        old_episodes = json.load(fl)
else:
    start_d = datetime(2020,10,1)

    h = Hive()
    old_episodes = []
    for acc in accs:
        account = Account(acc)
        c_list= {}
        for c in map(Comment, account.history(only_ops=["comment"],start=start_d)):
            tags = c['tags']
            if 'pod2hive' in tags:        
                if c.permlink in c_list:
                    continue
                try:
                    c.refresh()
                except ContentDoesNotExistsException:
                    continue
                c_list[c.permlink] = 1
                if not c.is_comment():
                    episode = {
                        'title' : c.title,
                        'permlink' : c.permlink,
                        'author' : c.authorperm
                        }       
                    old_episodes.append(episode)
                    tags = c['tags']
                    print(f'{c.title} - {c.permlink} - {tags}')
                    # print(f'')


    print(json.dumps(old_episodes, indent=2))
    with open('old_episodes.json', 'w') as fl:
        json.dump(old_episodes,fl, indent=2)

find_this = 'Episode 18: Taking a Tenet'
this_one = next((item for item in old_episodes if item["title"] == find_this), False)
if this_one:
    print(this_one['permlink'])

    
                
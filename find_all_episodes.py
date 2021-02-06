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

force_reload = False
update_only = not force_reload

if not force_reload and os.path.exists('old_episodes.json'):
    with open('old_episodes.json','r') as fl:
        old_episodes = json.load(fl)
else:
    old_episodes = []
    
        
        

start_d = datetime(2020,10,1)
# h = Hive()
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
                    'author' : c.authorperm,
                    'timestamp' : c.get('timestamp'), 
                    'url' : c.get('url')
                    }       
                old_episodes.append(episode)
                tags = c['tags']
                print(f'{c.title} - {c.permlink} - {tags}')
                # print(f'')


print(json.dumps(old_episodes, indent=2))
with open('old_episodes.json', 'w') as fl:
    json.dump(old_episodes,fl, indent=2)


                
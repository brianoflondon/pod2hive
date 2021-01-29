
import json
import hashlib

with open('no-agenda.json', 'r') as fl:
    epi = json.load(fl)

hashtab = {}
    
for it in epi['items']:
    guid = it.get('guid')
    print(guid)
    m = hashlib.md5()
    m.update(guid.encode())
    hashstr = m.hexdigest()[:8]
    print(hashstr)
    hashtab[guid] = hashstr
    
print(json.dumps(hashtab, indent=2))
print(hashlib.algorithms_guaranteed)
print(m.digest_size)
print(m.block_size)

guid = 'http://1290.noagendanotes.com/'

guid ='in the morning'
m = hashlib.md5()
m.update(guid.encode())
print(m.hexdigest())
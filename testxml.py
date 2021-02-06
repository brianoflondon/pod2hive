import xml.etree.ElementTree as ET
import requests
from bs4 import BeautifulSoup as bs
import xmltodict
import json


def print_all(children):
    # print(children.tag, ' -> ', children.attrib, ' |')
    for item in children:
        if item.tag == '{https://podcastindex.org/namespace/1.0}value' or item.tag == '{https://podcastindex.org/namespace/1.0}valueRecipient':
            print(item.tag, ' -> ', item.attrib)
        print_all(item)


url = 'http://hive.noagendahost.com/@brianoflondon'

xml_text = requests.get(url=url).text

root = ET.fromstring(xml_text)
children = root.getchildren()


ns = {'podcast': 'https://podcastindex.org/namespace/1.0.dtd'}

# for value in root.findall('podcast:value', ns):

for value in root.findall('{https://podcastindex.org/namespace/1.0}value'):
    print(value.tag, value.attrib)
    # name = actvaor.find('real_person:name', ns)
    # print(name.text)
    # for char in actor.findall('role:character', ns):
    #     print(' |-->', char.text)

print(root.findall('{https://podcastindex.org/namespace/1.0}value'))

print_all(root)



bs_cont = bs(xml_text, "lxml")
result = bs_cont.find_all('podcast:value')
hbd = bs_cont.find_all('HBD')

print(result)
print(bs_cont)

dict_data = xmltodict.parse(xml_text)
value = dict_data['rss']['channel'].get('podcast:value')
print(json.dumps(value,indent=2))
try:
    email = dict_data['rss']['channel']['podcast:locked']['@owner']
except:
    email = ''
    
print(email)
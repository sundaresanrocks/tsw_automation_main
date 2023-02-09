# import pymongo
import redis

import runtime
from lib.canon import url_canon
from lib.db.mongowrap import get_qa_mongo_wrap

red = redis.StrictRedis()
# red = redis.StrictRedis(host='localhost', port=6379, db=0)

mng = get_qa_mongo_wrap('top_site', 'db_top_site')

ALEXA_FILE = runtime.src_path + '/tsw/prevalence/alexa_1m.txt'
ALEXA_FILE = '/tmp/a1m.txt'
#ALEXA_FILE = '/tmp/alexa_top_1000000.txt'

err_no_url = []
err_list_data = []
err_rank = []
err_value = []

#mcl = mng.get_collection_obj()

def get_alx_rank(lst):
    for dat in lst:
        rnk = None
        if 'source' in dat and \
                   dat['source'] == 'alexa' and \
                   'name' in dat and \
                   dat['name'] == 'top_1m':
            rnk = dat['ranking'] if 'ranking' in dat else None
    return rnk

for url_line in open(ALEXA_FILE).readlines():
    rank, _, url = url_line.strip().rpartition(',')
    urld = url_canon(url)
    red.hset(urld['sha256'],'org', urld['url'])
    red.hset(urld['sha256'],'url', urld['url'])
    red.hset(urld['sha256'],'rank_f',rank)
    red.hset(urld['sha256'],'db_hash',urld['db_hash'])


def alx_diff():
    def _print(msg, lst):
        print(('\n' + msg))
        for itms in lst:
            print((': '.join([str(itm) for itm in itms])))

    for _url_line in open(ALEXA_FILE).readlines():
        _rank, _, _url = _url_line.strip().rpartition(',')
        _urld = url_canon(_url)
        _urld['alexa_rank'] = _rank
        doc = mng.query_one('{"_id":"%s"}' % _urld['sha256'])
        if not doc:
            err_no_url.append((_rank, _url))
            continue
        if not ('url' in doc and doc['url'] == _urld['url']):
            err_value.append((_urld['url'], 'URL'))
            continue
        key = 'in_alexa'
        has_key = key in doc
        if not (key in doc and doc[key]):
            err_value.append((_urld['url'],
                              key,
                              'True',
                              doc[key] if key in doc else 'None'))
            continue
        key = 'db_hash'
        has_key = key in doc
        if not ( has_key and doc[key] == _urld[key]):
            err_value.append((_urld['url'],
                              key, 
                              _urld[key],
                              doc[key] if key in doc else 'None'))
            continue
        key = 'list_data'
        has_key = key in doc
        if not (has_key and len(doc[key]) >= 1):
            err_list_data.append((_urld['url'],
                                  key,
                                  doc[key] if key in doc else 'None'))
            continue
        alx_rank = get_alx_rank(doc['list_data'])
        if int(alx_rank) != int(_rank):
            err_rank.append((_urld['url'],
                                  'rank',
                                  _rank,
                                  alx_rank
                             ))

    E_URL = '''Missing URLs
    -----------------------------------------------------------------------------'''
    E_VAL = '''Value Mismatch
    -----------------------------------------------------------------------------'''
    E_LST = '''Zero/No list data
    -----------------------------------------------------------------------------'''
    E_RNK = '''Rank Mismatch
    -----------------------------------------------------------------------------'''
    _print(E_URL, err_no_url)
    _print(E_VAL, err_value)
    _print(E_LST, err_list_data)
    _print(E_RNK, err_rank)


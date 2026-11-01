"""Optional OpenSearch REST indexing and search; requires running service."""
import json
import os
from dataclasses import asdict
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import quote

BASE = os.environ.get('OPENSEARCH_URL','http://localhost:9200').rstrip('/')
INDEX = 'cassandra-demo-logs'
MAPPING = {'mappings': {'properties': {
    'timestamp': {'type':'date'}, 'level':{'type':'keyword'}, 'node':{'type':'keyword'},
    'thread':{'type':'keyword'}, 'source':{'type':'keyword'}, 'message':{'type':'text'}
}}}

def request(method, url, body=None):
    data=json.dumps(body).encode() if body is not None else None
    req=Request(BASE+url, data=data, method=method, headers={'Content-Type':'application/json'})
    try:
        with urlopen(req,timeout=10) as resp:
            return json.loads(resp.read() or b'{}')
    except HTTPError as e:
        if e.code==400 and 'resource_already_exists_exception' in e.read().decode():
            return {'acknowledged':True}
        raise

def index_records(records):
    request('PUT','/'+INDEX,MAPPING)
    for item in records:
        request('POST','/'+INDEX+'/_doc',asdict(item))
    request('POST','/'+INDEX+'/_refresh')
    return len(records)

def search_records(level='',node='',q='',size=200):
    filters=[]
    if level: filters.append({'term':{'level':level}})
    if node: filters.append({'term':{'node':node}})
    query={'bool':{'filter':filters,'must':[{'multi_match':{'query':q,'fields':['message','source']}}] if q else [{'match_all':{}}]}}
    result=request('POST','/'+INDEX+'/_search',{'size':max(1,min(size,1000)),'sort':[{'timestamp':'desc'}],'query':query})
    return [hit['_source'] for hit in result.get('hits',{}).get('hits',[])]

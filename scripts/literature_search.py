#!/usr/bin/env python3
import json, urllib.parse, urllib.request, xml.etree.ElementTree as ET, time
from pathlib import Path

QUERIES = [
    'all:Collatz',
    'all:"3x+1"',
    'all:"Sturmian words" AND all:"irrational rotation"',
    'all:"return words" AND all:Sturmian',
    'all:"p-adic" AND all:Collatz',
    'all:"Diophantine approximation" AND all:"log 2" AND all:"log 3"',
]

NS={'a':'http://www.w3.org/2005/Atom'}
rows=[]
for q in QUERIES:
    url='https://export.arxiv.org/api/query?'+urllib.parse.urlencode({'search_query':q,'start':0,'max_results':12,'sortBy':'submittedDate','sortOrder':'descending'})
    req=urllib.request.Request(url,headers={'User-Agent':'CEREBRON-Literature-Farm/1.0'})
    try:
        with urllib.request.urlopen(req,timeout=30) as r:
            data=r.read()
        root=ET.fromstring(data)
        for e in root.findall('a:entry',NS):
            title=' '.join((e.findtext('a:title',default='',namespaces=NS) or '').split())
            summary=' '.join((e.findtext('a:summary',default='',namespaces=NS) or '').split())
            published=e.findtext('a:published',default='',namespaces=NS)
            link=e.findtext('a:id',default='',namespaces=NS)
            authors=[a.findtext('a:name',default='',namespaces=NS) for a in e.findall('a:author',NS)]
            rows.append({'query':q,'title':title,'authors':authors,'published':published,'url':link,'summary':summary})
    except Exception as exc:
        rows.append({'query':q,'error':repr(exc)})
    time.sleep(1)

# dedupe by url/title
seen=set(); out=[]
for r in rows:
    k=r.get('url') or (r.get('query'),r.get('title'))
    if k in seen: continue
    seen.add(k); out.append(r)
Path('literature-results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'records':len(out),'queries':len(QUERIES)}))

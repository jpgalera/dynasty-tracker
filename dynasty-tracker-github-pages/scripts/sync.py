#!/usr/bin/env python3
"""Fetch public Armory JSON routes, validate, normalize, and store dated snapshots.
Runs in GitHub Actions with no credentials. Never commits partial/failed results.
"""
import datetime as dt
import json
import os
import pathlib
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
CHARACTER = os.environ.get('DYNASTY_CHARACTER', 'lXlGhostlXl')
ORIGIN = 'https://armory.cabaldynasty.to'
ROUTES = ['character','summary','gear','stellar','forcewing','merit','runes','collection','creation','achievements','mercenaries','quickslots','eventpass','costume']
REQUIRED = {'character','summary','gear','stellar','forcewing','merit','runes','collection'}

def fetch(route):
    url = ORIGIN + '/api/' + route + '?' + urllib.parse.urlencode({'name': CHARACTER})
    req = urllib.request.Request(url, headers={'Accept':'application/json','User-Agent':'DynastyTracker/1.0 (+GitHub Actions; personal public-armory dashboard)'})
    with urllib.request.urlopen(req,timeout=25) as response:
        if response.status != 200: raise RuntimeError(f'{route}: HTTP {response.status}')
        content=response.read(8_000_001)
        if len(content)>8_000_000: raise RuntimeError(f'{route}: response too large')
        return json.loads(content)

def normalize(r, stamp):
    get=lambda k:r.get(k) or {}
    g,fw,st,co,ru,me,a=[get(k) for k in ('gear','forcewing','stellar','collection','runes','merit','achievements')]
    return {'id':stamp,'date':stamp,'data':{'character':get('character'),'summary':get('summary'),
        'gear':[{'slot':x.get('label'),'name':(x.get('piece') or {}).get('text',''),'effects':(x.get('piece') or {}).get('effects',[])} for x in (g.get('board') or {}).get('cells',[])],
        'pet':(g.get('pet') or {}).get('pet') or {},
        'forcewing':{k:fw.get(k) for k in ['gradeName','level','exp','expNext','expPct','score','slots','presets']},
        'stellar':st.get('lines',[]),'collections':co.get('pages',[]),'books':co.get('books',[]),
        'runes':{k:(ru.get(k) or {}).get('runes',[]) for k in ['essence','blended','karma']},
        'merit':me.get('badges',[]),
        'achievements':{k:a.get(k) for k in ['points','earned','total','percent']}}}

def main():
    results={}
    for route in ROUTES:
        try:
            results[route]=fetch(route)
            print(f'{route}: OK')
        except (urllib.error.URLError,ValueError,RuntimeError,TimeoutError) as exc:
            if route in REQUIRED: raise RuntimeError(f'Required endpoint {route} failed: {exc}') from exc
            print(f'{route}: optional endpoint unavailable: {exc}')
        time.sleep(.4)
    if not isinstance(results['character'],dict) or not results['character']:
        raise RuntimeError('Character payload invalid; refusing to save snapshot')
    if not isinstance(results['collection'],dict) or not isinstance(results['collection'].get('pages'),list):
        raise RuntimeError('Collection payload invalid; refusing to save snapshot')
    now=dt.datetime.now(dt.timezone.utc)
    stamp=now.isoformat(timespec='seconds').replace('+00:00','Z')
    snapshot=normalize(results,stamp)
    # One snapshot per UTC day, overwritten on subsequent successful runs that day.
    filename=now.strftime('%Y-%m-%d')+'.json'
    folder=DATA/'snapshots';folder.mkdir(parents=True,exist_ok=True)
    target=folder/filename
    manifest_path=DATA/'index.json'
    manifest=json.loads(manifest_path.read_text()) if manifest_path.exists() else {'snapshots':[]}
    entries=[e for e in manifest.get('snapshots',[]) if e.get('path')!='snapshots/'+filename]
    entries.append({'id':stamp,'date':stamp,'path':'snapshots/'+filename})
    entries.sort(key=lambda x:x['date'])
    # Keep last 120 daily snapshots; delete older files from the repository.
    expired=entries[:-120]
    entries=entries[-120:]
    target.write_text(json.dumps(snapshot,ensure_ascii=False,separators=(',',':'))+'\n')
    for item in expired:
        old=DATA/item['path']
        if old.is_file() and old.resolve().is_relative_to(folder.resolve()):old.unlink()
    manifest_path.write_text(json.dumps({'updatedAt':stamp,'character':CHARACTER,'snapshots':entries},indent=2)+'\n')
    print(f'Saved {filename}; total snapshots {len(entries)}')

if __name__=='__main__':main()

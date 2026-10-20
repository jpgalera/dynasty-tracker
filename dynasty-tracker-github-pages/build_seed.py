import json,glob
p=glob.glob('/mnt/data/cabal_dynasty*json')[-1];d=json.load(open(p));r=d['results']
def val(k):return r.get(k,{}).get('data') or {}
def compact():
 g=val('gear');fw=val('forcewing');st=val('stellar');co=val('collection');ru=val('runes');me=val('merit');a=val('achievements')
 return dict(character=val('character'),summary=val('summary'),gear=[{'slot':x['label'],'name':x.get('piece',{}).get('text','') if x.get('piece') else '', 'effects':x.get('piece',{}).get('effects') if x.get('piece') else None} for x in g.get('board',{}).get('cells',[])],pet=g.get('pet',{}).get('pet',{}),forcewing={k:fw.get(k) for k in ['gradeName','level','exp','expNext','expPct','score','slots','presets']},stellar=st.get('lines',[]),collections=co.get('pages',[]),books=co.get('books',[]),runes={k:ru.get(k,{}).get('runes',[]) for k in ['essence','blended','karma']},merit=me.get('badges',[]),achievements={k:a.get(k) for k in ['points','earned','total','percent']})
seed={'id':d['exportedAt'],'date':d['exportedAt'],'data':compact()}
open('/mnt/data/dynasty-tracker/seed.js','w').write('window.DYNASTY_SEED='+json.dumps(seed,separators=(',',':'))+';')
print('seed bytes',len(open('/mnt/data/dynasty-tracker/seed.js').read()))

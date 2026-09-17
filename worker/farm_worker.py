#!/usr/bin/env python3
import json, subprocess
PREFERRED=['/generate','/chat','/predict','/respond','/infer','/run']
def run(cmd,t=240): return subprocess.run(cmd,capture_output=True,text=True,timeout=t)
def payload(spec,prompt):
    p={}; setp=False
    for x in spec.get('parameters',[]):
        n=x.get('name',''); l=n.lower(); req=bool(x.get('required')); d=x.get('default'); typ=(x.get('type') or {}).get('type')
        if l in {'message','prompt','text','query','input','instruction','user_message'}: p[n]=prompt; setp=True
        elif l in {'chat_history','history','messages'}: p[n]=[]
        elif l in {'max_new_tokens','max_tokens','maximum_new_tokens'}: p[n]=700
        elif l=='temperature': p[n]=0.1
        elif l=='top_p': p[n]=0.9
        elif req and d is None:
            if typ=='string' and not setp: p[n]=prompt; setp=True
            else: return None
    return p if setp else None
def invoke(space,prompt):
    i=run(['hf-gradio','info',space],120)
    if i.returncode: return False,'',{'stage':'info','error':(i.stderr or i.stdout)[-1000:]}
    try: api=json.loads(i.stdout)
    except Exception as e: return False,'',{'stage':'decode','error':repr(e)}
    eps=list(api.items()); eps.sort(key=lambda kv:(PREFERRED.index(kv[0]) if kv[0] in PREFERRED else 99,kv[0]))
    for ep,spec in eps:
        pl=payload(spec,prompt)
        if pl is None: continue
        r=run(['hf-gradio','predict',space,ep,json.dumps(pl,ensure_ascii=False)],240)
        if r.returncode==0 and r.stdout.strip(): return True,r.stdout.strip(),{'endpoint':ep}
    return False,'',{'stage':'predict','error':'no compatible endpoint'}

"""Small lossless-value KiCad S-expression helpers for additive schematic edits."""
import json
import re

class Atom(str):
    pass

def parse(text):
    stack=[];root=None
    for token in re.findall(r'"(?:\\.|[^"\\])*"|\(|\)|[^\s()]+',text):
        if token=='(':
            value=[]
            if stack:stack[-1].append(value)
            else:root=value
            stack.append(value)
        elif token==')':stack.pop()
        else:stack[-1].append(json.loads(token) if token.startswith('"') else Atom(token))
    assert not stack
    return root

def dump(value,level=0):
    if isinstance(value,list):
        if not any(isinstance(v,list) for v in value):return '('+' '.join(dump(v) for v in value)+')'
        return '('+' '.join(dump(v) for v in value if not isinstance(v,list))+''.join('\n'+'  '*(level+1)+dump(v,level+1) for v in value if isinstance(v,list))+')'
    return str(value) if isinstance(value,Atom) else json.dumps(value,ensure_ascii=False) if isinstance(value,str) else str(value)

def node(tag,*args):return [Atom(tag),*args]
def get(value,tag):return next((v for v in value if isinstance(v,list) and v and v[0]==tag),None)
def nodes(value,tag):return [v for v in value if isinstance(v,list) and v and v[0]==tag]
def num(value):return Atom(f'{value:.6f}'.rstrip('0').rstrip('.') if value else '0')
def pins(symbol):return [p for s in nodes(symbol,'symbol') for p in nodes(s,'pin')]
def effects(size=1,justify=None,hide=False):
    value=node('effects',node('font',node('size',num(size),num(size))))
    if justify:value.append(node('justify',Atom(justify)))
    if hide:value.append(node('hide',Atom('yes')))
    return value

"""Create standalone native KiCad schematics for the explicit power test circuits.

The test circuit is a named SPICE subcircuit, not a model of the complete PCB.
All model content is local; no absolute machine paths are stored in schematics.
"""
from pathlib import Path
import json,uuid
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'kicad';MODELS=OUT/'bench_models'
q=lambda s:json.dumps(str(s),ensure_ascii=False)
uid=lambda s:str(uuid.uuid5(uuid.NAMESPACE_URL,'vptc-v2-simulation/'+s))

def build(deck):
    name=deck.stem;root_id=uid(name);symbol_id=uid(name+'/X1')
    directives=[];body=[]
    for line in deck.read_text().splitlines()[1:]:
        if line.lower().startswith(('.include','.end','.save')):continue
        if line.lower().startswith(('.param','.options','.tran')):directives.append(line);continue
        if line.startswith('*') or not line.strip():body.append(line);continue
        tokens=line.split();npins=5 if tokens[0].startswith('X') else 2
        for i in range(1,npins+1):
            if tokens[i]=='0':tokens[i]='GND'
        body.append(' '.join(tokens))
    model='ENCODER_V2_POWER_BENCH'
    model_text=(ROOT/'power/vendor/tps7a20-adj_trans_ngspice.lib').read_text(errors='replace')
    model_text+='\n* Explicit equivalent load and lumped parasitics; no extracted PCB model.\n'
    model_text+=f'.subckt {model} VSRC VIN VOUT REMOTE LOADCMD GND\n'+'\n'.join(body)+'\n.ends '+model+'\n'
    (MODELS/(name+'.lib')).write_text(model_text)
    pins=[('1','VSRC',-17.78,7.62,0),('2','VIN',17.78,7.62,180),('3','VOUT',17.78,0,180),('4','REMOTE',17.78,-7.62,180),('5','LOADCMD',-17.78,0,0),('6','0',-17.78,-7.62,0)]
    effects='(effects (font (size 1.05 1.05)))'
    props=f'(property "Reference" "X" (at 0 15.24 0) {effects}) (property "Value" "Power test circuit" (at 0 12.7 0) {effects})'
    libpins=' '.join(f'(pin passive line (at {x} {y} {a}) (length 2.54) (name {q(net if net!="0" else "GND")} {effects}) (number {q(n)} {effects}))' for n,net,x,y,a in pins)
    lib=f'(symbol "Encoder_Test:PowerBench" (pin_names (offset .5)) (in_bom no) (on_board no) {props} (symbol "PowerBench_0_1" (rectangle (start -15.24 10.16) (end 15.24 -10.16) (stroke (width .254) (type default)) (fill (type background)))) (symbol "PowerBench_1_1" {libpins}))'
    inst=f'(symbol (lib_id "Encoder_Test:PowerBench") (at 100 70 0) (unit 1) (in_bom no) (on_board no) (dnp no) (uuid "{symbol_id}")'
    for key,val,x,y in [('Reference','X1',100,53),('Value','Power test circuit',100,56),('Sim.Library','bench_models/'+name+'.lib',100,70),('Sim.Name',model,100,70),('Sim.Pins','1=1 2=2 3=3 4=4 5=5 6=6',100,70)]:
        hide=' (hide yes)' if key.startswith('Sim.') else ''
        inst+=f'(property {q(key)} {q(val)} (at {x} {y} 0) (effects (font (size 1.05 1.05)){hide}))'
    for n,*_ in pins:inst+=f'(pin {q(n)} (uuid "{uid(name+"/pin/"+n)}"))'
    inst+=f'(instances (project {q(name)} (path "/{root_id}" (reference "X1") (unit 1)))))'
    labels=[]
    for n,net,x,y,a in pins:
        px=100+x;py=70-y;ex=px+(-7.62 if x<0 else 7.62)
        labels.append(f'(wire (pts (xy {px} {py}) (xy {ex} {py})) (stroke (width 0) (type default)) (uuid "{uid(name+"/wire/"+n)}"))')
        labels.append(f'(global_label {q(net)} (shape bidirectional) (at {ex} {py} 0) (effects (font (size 1.05 1.05)) (justify {"left" if x<0 else "right"})) (uuid "{uid(name+"/label/"+n)}"))')
    directives.append('.save v(VSRC) v(VIN) v(VOUT) v(REMOTE) v(LOADCMD)')
    texts=[]
    for i,text in enumerate(['\n'.join(directives),'Equivalent power circuit from V2 values.\nX1 contains the TI LDO model, capacitors, wiring R/L and electronic load.\nPlot V(REMOTE) for the voltage at the load; V(VOUT) is the LDO output.\nMCU firmware, CAN protocol, Hall conversion and PCB geometry are not simulated.']):
        texts.append(f'(text {q(text)} (at 35 {105+i*25} 0) (effects (font (size 1.15 1.15)) (justify left)) (uuid "{uid(name+"/text/"+str(i))}"))')
    sch=f'(kicad_sch (version 20250114) (generator "encoder_v2_simulation") (uuid "{root_id}") (paper "A4") (title_block (title {q("Encoder V2 power simulation: "+name)}) (date "2026-10-16")) (lib_symbols {lib}) '+inst+' '+' '.join(labels+texts)+')\n'
    (OUT/(name+'.kicad_sch')).write_text(sch)
    pro={'meta':{'filename':name+'.kicad_pro','version':1},'schematic':{'ngspice':{'meta':{'version':0},'fix_include_paths':True,'fix_passive_vals':True,'model_mode':2,'workbook_filename':''}}}
    (OUT/(name+'.kicad_pro')).write_text(json.dumps(pro,indent=2)+'\n')

def main():
    MODELS.mkdir(parents=True,exist_ok=True)
    for deck in sorted((ROOT/'power/netlists').glob('*.cir')):
        if deck.stem not in ['model_steady_sanity','load_step_refined_50ns']:build(deck)
    print('Native KiCad benches generated:',len(list(OUT.glob('*.kicad_sch'))))

if __name__=='__main__':main()

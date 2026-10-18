"""Native KiCad ngspice RC sensitivity checks, from the exported V2 netlist."""
from pathlib import Path
import csv,hashlib,json,sys,xml.etree.ElementTree as ET
import numpy as np
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'power'))
from run_power import NgSpice

def value(s):
    import re
    m=re.fullmatch(r'([0-9.]+)([pnumk]?)(?:[FOhms]*)',s)
    if not m:raise ValueError(s)
    return float(m[1])*{'':1,'p':1e-12,'n':1e-9,'u':1e-6,'m':1e-3,'k':1e3}[m[2]]

def source_check():
    import subprocess
    board=ROOT.parent
    subprocess.run(['/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli','sch','export','netlist',str(board/'encoder_can_v2.kicad_sch'),'--format','kicadxml','-o',str(ROOT/'source_netlist.xml')],check=True,capture_output=True)
    doc=ET.parse(ROOT/'source_netlist.xml').getroot()
    components={c.get('ref'):c.findtext('value') for c in doc.findall('components/comp')}
    nets={(n.get('ref'),n.get('pin')):net.get('name') for net in doc.findall('nets/net') for n in net.findall('node')}
    spec=json.loads((board/'design/electrical_spec.json').read_text())
    for c in spec['components']:
        assert c['value']==components[c['ref']],c['ref']
        for pin,net in c['pins'].items():
            actual=nets.get((c['ref'],pin))
            if net is not None:assert actual==net,(c['ref'],pin,actual,net)
            else:assert actual is None or actual.startswith('unconnected-'),(c['ref'],pin,actual)
    nominal=sum(value(components[c['ref']]) for c in spec['components'] if c['ref'].startswith('C') and c['pins'].get('1')=='+3V3' and c['pins'].get('2')=='GND')
    assert abs(nominal-11.91e-6)<1e-12
    result={'date':'2026-10-16','component_values_and_connected_pin_nets_match_spec':True,'nominal_3v3_capacitance_f':nominal,'source_sha256':{name:hashlib.sha256((board/name).read_bytes()).hexdigest() for name in ['encoder_can_v2.kicad_sch','encoder_can_v2.kicad_pcb','design/electrical_spec.json']},'xml_sha256':hashlib.sha256((ROOT/'source_netlist.xml').read_bytes()).hexdigest()}
    (ROOT/'source_check.json').write_text(json.dumps(result,indent=2)+'\n')
    return components

def crossing(t,y,threshold,start=0):
    ids=np.flatnonzero((t>=start)&(y>=threshold))
    if not len(ids):return None
    i=ids[0]
    if i==0:return float(t[i])
    return float(t[i-1]+(t[i]-t[i-1])*(threshold-y[i-1])/(y[i]-y[i-1]))

def run(ng,name,lines,signals,stop):
    path=ROOT/'interfaces'/name
    path.with_suffix('.cir').write_text('\n'.join(lines)+'\n')
    ng.command('destroy all');ng.log=[];ng.command('source '+str(path.with_suffix('.cir')));ng.command('run')
    path.with_suffix('.log').write_text('\n'.join(ng.log)+'\n')
    assert not any('aborted' in q.lower() or 'error' in q.lower() or 'timestep too small' in q.lower() for q in ng.log),ng.log[-20:]
    result={s:ng.vector(s) for s in ['time',*signals]}
    assert result['time'][-1]>=stop-1e-10
    np.savez_compressed(path.with_suffix('.npz'),**result)
    return result

def main():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    c=source_check();(ROOT/'interfaces').mkdir(exist_ok=True)
    ng=NgSpice();(ROOT/'interfaces/engine.log').write_text('\n'.join(ng.log)+'\n')
    lines=['V2 I2C RC sensitivity; driver switch is an assumption, not an IC model','Vdd vdd 0 3.3','Vgate gate 0 PULSE(1 0 1.5u 1n 1n 1u 2.5u)','.model OC SW(Ron=33 Roff=1e12 Vt=.5 Vh=0)']
    signals=[];cases=[]
    for n,ref in enumerate(['R1','R2','R3','R4']):
        for cp in [30,50,100,150,160]:
            name=f'bus{n}_{cp}';r=value(c[ref])*1.01
            lines += [f'R{name} vdd {name} {r}',f'C{name} {name} 0 {cp}p',f'S{name} {name} 0 gate 0 OC']
            signals.append(f'v({name})');cases.append((name,ref,cp,r))
    lines+=['.save v(gate) '+' '.join(signals),'.tran .5n 10u 0 .5n','.end']
    data=run(ng,'i2c',lines,['v(gate)',*signals],10e-6);t=data['time'];rows=[]
    for name,ref,cp,r in cases:
        y=data[f'v({name})'];a=crossing(t,y,.3*3.3,1.5e-6);b=crossing(t,y,.7*3.3,1.5e-6)
        rise=(b-a)*1e9;expected=np.log(7/3)*r*cp*1e-3
        assert abs(rise-expected)<.2,(rise,expected)
        rows.append({'pullup':ref,'assumed_line_cap_pf':cp,'r_worst_high_ohm':r,'rise_30_70_ns':rise,'independent_rc_ns':expected,'fast_mode_300ns_pass':bool(rise<=300)})
    (ROOT/'interfaces/i2c_results.json').write_text(json.dumps(rows,indent=2)+'\n')
    fig,ax=plt.subplots(1,2,figsize=(10,4),constrained_layout=True)
    for cp in [30,50,150,160]:
        mask=(t>=1.49e-6)&(t<=2.2e-6);ax[0].plot((t[mask]-1.5e-6)*1e9,data[f'v(bus0_{cp})'][mask],label=f'{cp} pF')
    for level in [.3*3.3,.7*3.3]:ax[0].axhline(level,color='#888888',ls='--',lw=.7)
    ax[0].set(xlabel='Time after release, ns',ylabel='I2C voltage, V',title='R1-R4: 2.2 kohm +1%');ax[0].legend();ax[0].grid(alpha=.2)
    lines=['V2 reset RC corners; POR/BOR and MCU are not modeled','Vdd vdd 0 3.3'];signals=[];rcases=[]
    for i,(rf,ri,cf) in enumerate((rf,ri,cf) for rf in [.99,1.01] for ri in [25000,55000] for cf in [.9,1.1]):
        r=value(c['R6'])*rf;cap=value(c['C12'])*cf;name=f'nrst{i}'
        lines +=[f'Rext{i} vdd {name} {r}',f'Rint{i} vdd {name} {ri}',f'Creset{i} {name} 0 {cap} IC=0']
        signals.append(f'v({name})');rcases.append((name,r,ri,cap))
    lines+=['.save '+' '.join(signals),'.tran .5u 5m 0 .5u uic','.end']
    reset=run(ng,'reset',lines,signals,.005);rr=[]
    for name,r,ri,cap in rcases:
        measured=crossing(reset['time'],reset[f'v({name})'],.7*3.3);expected=-np.log(.3)*(1/(1/r+1/ri))*cap
        assert abs(measured-expected)<1e-6
        rr.append({'name':name,'external_ohm':r,'assumed_internal_ohm':ri,'cap_f':cap,'t70_ms':measured*1e3,'independent_rc_ms':expected*1e3})
        ax[1].plot(reset['time']*1e3,reset[f'v({name})'],lw=1,alpha=.7)
    ax[1].axhline(.7*3.3,color='#555555',ls='--',label='70% VDD');ax[1].set(xlabel='Time after release, ms',ylabel='NRST voltage, V',title='Reset RC corners; POR/BOR excluded');ax[1].legend();ax[1].grid(alpha=.2)
    (ROOT/'interfaces/reset_results.json').write_text(json.dumps(rr,indent=2)+'\n');fig.savefig(ROOT/'interfaces/interfaces.png',dpi=180);plt.close(fig)
    summary={'i2c_simulated_lines':len(rows),'i2c_sensitivity_pass_up_to_pf':150,'i2c_160pf_fails':all(not q['fast_mode_300ns_pass'] for q in rows if q['assumed_line_cap_pf']==160),'i2c_max_sink_current_at_3p6v_a':3.6/(value(c['R1'])*.99),'reset_corners':len(rr),'reset_t70_range_ms':[min(q['t70_ms'] for q in rr),max(q['t70_ms'] for q in rr)],'limits':['Capacitances 30-160 pF are sensitivity assumptions, not PCB extraction.','I2C switch is an assumed 33 ohm open-drain equivalent, not STM32/TMAG transistor behavior.','Reset is an external RC plus datasheet pullup range; internal POR/BOR and firmware excluded.']}
    (ROOT/'interfaces/summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))

if __name__=='__main__':main()

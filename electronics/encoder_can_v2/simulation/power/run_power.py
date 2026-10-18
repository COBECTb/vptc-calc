#!/usr/bin/env python3
"""Run explicitly ported official TI TPS7A20 PSpice model through native shared ngspice.

Dependencies: Python 3, numpy, matplotlib; KiCad native libngspice and its code models.
The load is an explicit equivalent load, not transistor models of MCU/CAN/sensors.
"""
import argparse, ctypes as ct, csv, hashlib, json, os, sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent
LIB=Path('/Applications/KiCad/KiCad.app/Contents/Frameworks/libngspice.0.dylib')
MODELS=Path('/Applications/KiCad/KiCad.app/Contents/PlugIns/sim/ngspice')
TI_ORIGINAL=ROOT/'vendor/SBVM961/tps7a20-adj_trans.lib'
TI=ROOT/'vendor/tps7a20-adj_trans_ngspice.lib'
SPEC=ROOT.parents[1]/'design/electrical_spec.json'

class Vector(ct.Structure):
    _fields_=[('name',ct.c_char_p),('type',ct.c_int),('flags',ct.c_short),
              ('real',ct.POINTER(ct.c_double)),('complex',ct.c_void_p),('length',ct.c_int)]

class NgSpice:
    def __init__(self):
        self.log=[]
        self.lib=ct.CDLL(str(LIB))
        cb=ct.CFUNCTYPE(ct.c_int,ct.c_char_p,ct.c_int,ct.c_void_p)
        self.cb=cb(self.output)
        self.lib.ngSpice_Init.argtypes=[cb,*[ct.c_void_p]*6]
        self.lib.ngSpice_Init(self.cb,None,None,None,None,None,None)
        self.lib.ngSpice_Command.argtypes=[ct.c_char_p]
        self.lib.ngGet_Vec_Info.argtypes=[ct.c_char_p]
        self.lib.ngGet_Vec_Info.restype=ct.POINTER(Vector)
        self.command('version')
        self.command('set ngbehavior=ps')
        for model in sorted(MODELS.glob('*.cm')):
            self.command('codemodel '+str(model))
    def output(self,message,ident,user):
        self.log.append(message.decode(errors='replace'))
        return 0
    def command(self,text):
        return self.lib.ngSpice_Command(text.encode())
    def vector(self,name):
        p=self.lib.ngGet_Vec_Info(name.encode())
        if not p or not p.contents.real or p.contents.length<2:
            raise RuntimeError('Missing/empty simulation vector: '+name)
        return np.ctypeslib.as_array(p.contents.real,shape=(p.contents.length,)).copy()
    def run(self,path):
        self.command('destroy all')
        self.log=[]
        self.command('source '+str(path))
        self.command('run')
        if any('error' in line.lower() for line in self.log):
            raise RuntimeError('\n'.join(self.log))
        data={v:self.vector(v) for v in ['time','v(vsrc)','v(vin)','v(vout)','v(loadcmd)','i(vsource)']}
        if 'model_steady_sanity' not in path.name:
            data['v(remote)']=self.vector('v(remote)')
        self.complete=bool(data['time'][-1]>=.012-1e-9 and not any('aborted' in line.lower() or 'timestep too small' in line.lower() for line in self.log))
        return data

# Capacitances in farads. Nominal rail total is derived independently from spec below.
CAPS={
 'nominal': {'cin':4.7e-6,'local':4.7e-6,'remote':7.21e-6},
 'bias_25c': {'cin':2.2e-6,'local':2.914645e-6,'remote':4.864645e-6},
 'stress_derated': {'cin':1.30e-6,'local':1.65e-6,'remote':2.765e-6},
}
# bias_25c: C11/C3 use official 3.3V value. Other capacitances deliberately reduced.
# stress: C11/C3 2.29156uF min-typ temperature *0.9 tolerance *0.8 aging reserve =1.65uF.
# CIN at 5V and other rail capacitors are sensitivity assumptions, not guaranteed minima.

def pwl(points):
    return 'PWL('+' '.join(f'{t:.9g} {v:.9g}' for t,v in points)+')'

CASES=[
 dict(name='startup_fast_nominal',caps='nominal',supply=[(0,0),(.001,0),(.00101,5),(.012,5)],load=[(0,.06),(.012,.06)],kind='startup'),
 dict(name='startup_fast_derated',caps='stress_derated',supply=[(0,0),(.001,0),(.00101,5),(.012,5)],load=[(0,.15),(.012,.15)],kind='startup'),
 dict(name='startup_slow_5ms',caps='bias_25c',supply=[(0,0),(.001,0),(.006,5),(.012,5)],load=[(0,.06),(.012,.06)],kind='startup'),
 dict(name='load_60_to_150mA',caps='bias_25c',supply=[(0,0),(.001,0),(.00101,5),(.012,5)],load=[(0,.06),(.005,.06),(.00501,.15),(.008,.15),(.00801,.06),(.012,.06)],kind='load'),
 dict(name='load_30_to_150mA_derated',caps='stress_derated',supply=[(0,0),(.001,0),(.00101,4.5),(.012,4.5)],load=[(0,.03),(.005,.03),(.005001,.15),(.008,.15),(.008001,.03),(.012,.03)],kind='load'),
 dict(name='input_sag_5_to_4p5V',caps='stress_derated',supply=[(0,0),(.001,0),(.00101,5),(.005,5),(.00501,4.5),(.008,4.5),(.00801,5),(.012,5)],load=[(0,.15),(.012,.15)],kind='line'),
 dict(name='input_sag_outside_range_3V',caps='stress_derated',supply=[(0,0),(.001,0),(.00101,5),(.005,5),(.00501,3.0),(.008,3.0),(.00801,5),(.012,5)],load=[(0,.15),(.012,.15)],kind='fault'),
 dict(name='power_interruption_50us',caps='stress_derated',supply=[(0,0),(.001,0),(.00101,5),(.005,5),(.00505,0),(.0051,0),(.00515,5),(.012,5)],load=[(0,.15),(.012,.15)],kind='fault'),
 dict(name='source_2ohm_2uH_loadstep',caps='stress_derated',supply=[(0,0),(.001,0),(.00101,4.5),(.012,4.5)],load=[(0,.03),(.005,.03),(.005001,.15),(.008,.15),(.008001,.03),(.012,.03)],kind='load',rsource=2.0,lsource=2e-6),
 dict(name='overload_350mA_model_only',caps='stress_derated',supply=[(0,0),(.001,0),(.00101,5),(.012,5)],load=[(0,.06),(.005,.06),(.005001,.35),(.008,.35),(.008001,.06),(.012,.06)],kind='overload'),
 dict(name='distribution_0p2ohm_50nH_loadstep',caps='stress_derated',supply=[(0,0),(.001,0),(.00101,4.5),(.012,4.5)],load=[(0,.03),(.005,.03),(.005001,.15),(.008,.15),(.008001,.03),(.012,.03)],kind='load',rplane=.2,lplane=50e-9),
]

def make_netlist(case):
    c=CAPS[case['caps']]
    return f'''Encoder CAN power: {case['name']}
* TI SBVM961 port: S2 Ron/Roff and Von/Voff swapped to avoid ngspice reverse-R clamp bug.
* ngspice clamps new Ron to 1mohm; documented in model_port.md. V_out selects 3.3V.
.param V_out=3.3
.include "{TI}"
.options reltol=0.001 abstol=1e-9 vntol=1e-6 itl4=200 method=gear
Vsource vsrc 0 {pwl(case['supply'])}
Rsource vsrc source_l {case.get('rsource',.2)}
Lsource source_l vin {case.get('lsource',1e-6)}
XU5 vin 0 vin nc vout TPS7A20_ADJ_TRANS
* NC is unused model pin, matching DBV pin4.
Rnc nc 0 1e12
Rcin vin cin_esr .02
C10 cin_esr 0 {c['cin']}
* C11 is local LDO output cap; remaining 3V3 caps combined behind estimated trace impedance.
Rcout vout cout_esr .01323
C11 cout_esr 0 {c['local']}
Rplane vout remote_l {case.get('rplane',.05)}
Lplane remote_l remote {case.get('lplane',5e-9)}
Rremote remote remote_cap .01323
Cremote remote_cap 0 {c['remote']}
Vcommand loadcmd 0 {pwl(case['load'])}
* V2 sensitivity: all equivalent load is placed at the remote rail, after distribution R/L.
* Load current scales with the remote rail below 3.3V; no current is drawn at 0V.
Bload remote 0 I={{v(loadcmd)*min(max(v(remote)/3.3,0),1)}}
Rleak vout 0 1e9
.save v(vsrc) v(vin) v(vout) v(remote) v(loadcmd) i(vsource)
.tran .2u .012 0 .2u
.end
'''

def first_cross(t,y,level,start=0):
    ids=np.where((t>=start)&(y>=level))[0]
    return float(t[ids[0]]) if len(ids) else None

def summarize(case,data):
    t=data['time'];out=data['v(vout)'];remote=data['v(remote)'];vin=data['v(vin)'];src=data['v(vsrc)'];cmd=data['v(loadcmd)']
    settled=(t>.0035) if case['kind']!='startup' else (t>.010)
    transient=(t>.0045)&(t<.010)
    startup_end=first_cross(t,out,3.0)
    t10=first_cross(t,out,.33);t90=first_cross(t,out,2.97)
    slope=None if t10 is None or t90 is None else 2.64/((t90-t10)*1e3)
    row={'case':case['name'],'category':case['kind'],'cap_corner':case['caps'],
         'last_output_v':float(out[-1]),'settled_min_v':float(out[settled].min()),
         'settled_max_v':float(out[settled].max()),
         'transient_min_v':float(out[transient].min()),'transient_max_v':float(out[transient].max()),
         'input_min_in_event_v':float(vin[transient].min()),
         'first_3V_time_ms':None if startup_end is None else startup_end*1e3,
         'rise_10_90_ms':None if t10 is None or t90 is None else (t90-t10)*1e3,
         'rise_10_90_average_V_per_ms':slope,
         'tmag_ramp_below_3V_per_ms':None if slope is None else slope<3,
         'time_below_CAN_3V_during_event_us':float(np.trapezoid((out[transient]<3.).astype(float),t[transient])*1e6),
         'rail_floor_pass_in_event':bool(min(out[transient].min(),remote[transient].min())>=3.),
         'remote_transient_min_v':float(remote[transient].min()),
         'remote_transient_max_v':float(remote[transient].max()),
         'remote_last_v':float(remote[-1]),
         'peak_source_current_A':float(np.max(-data['i(vsource)'])),
         'rail_ceiling_pass_all_time':bool(max(out.max(),remote.max())<=3.6),
         'output_max_all_time_v':float(out.max()),
         'input_min_all_time_v':float(vin.min()),'input_max_all_time_v':float(vin.max()),
         'input_within_abs_limits':bool(vin.min()>=-.3 and vin.max()<=6.5),
         'input_within_recommended_ceiling':bool(vin.max()<=6.0),
         'maximum_load_A':float(cmd.max()),
         'output_minus_input_max_v':float(np.max(out-vin)),
         'solver_complete':bool(t[-1]>=.012-1e-9),'simulation_end_ms':float(t[-1]*1e3)}
    # A source drop at startup is excluded from functional-rail checks.
    return row


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--only',help='one named case');ap.add_argument('--max-step-us',type=float,default=.2);ap.add_argument('--output-tag',default='');args=ap.parse_args()
    for name in ['netlists','results','plots']:(ROOT/name).mkdir(exist_ok=True)
    ng=NgSpice();results=[]
    validate_model(ng)
    cases=[c for c in CASES if args.only is None or c['name']==args.only]
    if not cases:raise RuntimeError('Unknown case')
    for case in cases:
        path=ROOT/'netlists'/(case['name']+'.cir');path.write_text(make_netlist(case).replace('.tran .2u .012 0 .2u',f'.tran {args.max_step_us}u .012 0 {args.max_step_us}u'))
        try:data=ng.run(path)
        finally:(ROOT/'results'/(case['name']+'.log')).write_text('\n'.join(ng.log)+'\n')
        columns=list(data)
        arr=np.column_stack([data[k] for k in columns])
        np.savetxt(ROOT/'results'/(case['name']+'.csv'),arr,delimiter=',',header=','.join(columns),comments='')
        ng.command('set filetype=binary')
        ng.command('write '+str(ROOT/'results'/(case['name']+'.raw'))+' all')
        row=summarize(case,data)
        if not ng.complete:
            row['solver_complete']=False
            row['assessment']='UNSUPPORTED: transient aborted below VIN0.895V; partial vectors diagnostic only'
            for key in ['rail_floor_pass_in_event','rail_ceiling_pass_all_time','input_within_abs_limits','input_within_recommended_ceiling']:
                row[key]=None
        elif case['kind']=='overload':
            row['assessment']='MODEL ONLY: outside300mA operating rating; thermal model absent'
        elif case['kind']=='fault':
            row['assessment']='OUTSIDE BOARD INPUT RANGE: CAN undervoltage expected; not a normal operating pass'
        else:
            row['assessment']='COMPLETE: typical family-model sensitivity result; not hardware qualification'
        results.append(row)
        print(json.dumps(row),flush=True)
    (ROOT/'results'/('summary'+args.output_tag+'.json')).write_text(json.dumps(results,indent=2)+'\n')
    with (ROOT/'results'/('summary'+args.output_tag+'.csv')).open('w',newline='') as stream:
        w=csv.DictWriter(stream,fieldnames=results[0],lineterminator='\n');w.writeheader();w.writerows(results)
    spec=json.loads(SPEC.read_text())
    caps=[c for c in spec['components'] if c['ref'].startswith('C') and c['pins'].get('1')=='+3V3' and c['pins'].get('2')=='GND']
    manifest={'simulator':'ngspice 45.2 shared library from KiCad native app','lib':str(LIB),'compatibility':'PSpice ps; bundled KiCad XSPICE codemodels loaded',
              'model_url':'https://www.ti.com/lit/zip/sbvm961','ported_model_sha256':hashlib.sha256(TI.read_bytes()).hexdigest(),
              'original_model_sha256':hashlib.sha256(TI_ORIGINAL.read_bytes()).hexdigest(),
              'zip_sha256':hashlib.sha256((ROOT/'vendor/SBVM961.zip').read_bytes()).hexdigest(),
              'spec_sha256':hashlib.sha256(SPEC.read_bytes()).hexdigest(),'model_modified':True,'family_configuration':'2020 generic family typical model V_out=3.3; not a PDBV corner model',
              'port_modification':'S2 Ron/Roff and Von/Voff swapped; simulator Ron lower clamp adds at most0.15mV to output drop at150mA in steady on state',
              'rail_cap_refs':[c['ref'] for c in caps],'cap_corners':CAPS,'scenarios':cases,
              'load_location':'Entire equivalent load placed on remote rail after lumped distribution R/L; V2 rerun, not reuse of V1 results.',
              'source_pcb_sha256':hashlib.sha256((SPEC.parent.parent/'encoder_can_v2.kicad_pcb').read_bytes()).hexdigest(),
              'source_schematic_sha256':hashlib.sha256((SPEC.parent.parent/'encoder_can_v2.kicad_sch').read_bytes()).hexdigest(),
              'limits':['Temperature and quiescent current explicitly not modeled by TI.','No thermal/package/layout extraction, no actual MCU/CAN/sensor load model.','Capacitance corners and lumped parasitics are explicit sensitivity assumptions, not guaranteed manufacturing corners.']}
    (ROOT/'results/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    make_plots(cases)

def make_plots(cases):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size':9,'axes.grid':True,'grid.alpha':.25,'figure.dpi':160})
    for case in cases:
        path=ROOT/'results'/(case['name']+'.csv');d=np.loadtxt(path,delimiter=',',skiprows=1)
        fig,ax=plt.subplots(2,1,figsize=(8,5),sharex=True,gridspec_kw={'height_ratios':[3,1]})
        ax[0].plot(d[:,0]*1e3,d[:,1],label='Supply before wiring');ax[0].plot(d[:,0]*1e3,d[:,2],label='LDO VIN');ax[0].plot(d[:,0]*1e3,d[:,3],label='LDO output');ax[0].plot(d[:,0]*1e3,d[:,6],label='Remote 3V3 load')
        ax[0].axhline(3.,color='red',ls='--',lw=.8,label='CAN minimum supply 3.0 V')
        ax[0].set_ylabel('Voltage, V');ax[0].legend(loc='lower right',fontsize=8,ncol=2)
        ax[1].plot(d[:,0]*1e3,d[:,4]*1e3,label='Load command');ax[1].set_ylabel('Load, mA');ax[1].set_xlabel('Time, ms')
        fig.suptitle(case['name']+' | TI model, documented ngspice port | '+case['caps']+(' | INCOMPLETE DIAGNOSTIC' if d[-1,0]<.011999 else ''))
        fig.tight_layout();fig.savefig(ROOT/'plots'/(case['name']+'.png'));fig.savefig(ROOT/'plots'/(case['name']+'.svg'));plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,4))
    for case in cases:
        if case['kind']!='load':continue
        d=np.loadtxt(ROOT/'results'/(case['name']+'.csv'),delimiter=',',skiprows=1)
        mask=(d[:,0]>.0049)&(d[:,0]<.0056)
        ax.plot((d[mask,0]-.005)*1e6,d[mask,6],label=case['name'])
    ax.axhline(3.,color='red',ls='--',lw=.8,label='CAN min 3.0 V');ax.set_xlabel('Time from load step, us');ax.set_ylabel('3V3 output, V');ax.legend(fontsize=7)
    fig.tight_layout();fig.savefig(ROOT/'plots/load_step_comparison.png');fig.savefig(ROOT/'plots/load_step_comparison.svg')

def validate_model(ng):
    p=ROOT/'netlists/model_steady_sanity.cir'
    p.write_text(f'''Model sanity 3.3V/60mA equivalent resistive load
.param V_out=3.3
.include "{TI}"
.options method=gear reltol=.0001
Vsource vsrc 0 PWL(0 0 1m 0 1.01m 5 12m 5)
Rwire vsrc vin .000001
XU5 vin 0 vin nc vout TPS7A20_ADJ_TRANS
C10 vin 0 4.7u
C11 vout 0 8u
Rload vout 0 55
Vcommand loadcmd 0 .06
.save v(vsrc) v(vin) v(vout) v(loadcmd) i(vsource)
.tran 1u 12m
.end
''')
    d=ng.run(p);out=float(d['v(vout)'][-1])
    (ROOT/'results/model_steady_sanity.log').write_text('\n'.join(ng.log)+'\n')
    if not ng.complete or not 3.2<out<3.4:
        raise RuntimeError(f'Model sanity FAILED, Vout={out} V. No suite results accepted.')
    (ROOT/'results/model_steady_sanity.json').write_text(json.dumps({'vout_last_v':out,'pass':True,'criterion_v':[3.2,3.4]},indent=2)+'\n')

if __name__=='__main__':main()

#!/usr/bin/env python3
"""Reproduce the S2 compatibility diagnostic and independent loaded output sanity."""
import json, numpy as np
from run_power import NgSpice, ROOT, TI, TI_ORIGINAL

def switch_resistance(control,ron,roff,clamp=False):
    # PSpice smooth logarithmic transition, also used by ngspice pswitch.
    if clamp:ron=max(ron,.001)
    on,off=(.001,0) if ron>roff else (0,.001)
    u=np.clip((control-off)/(on-off),0,1)-.5
    return np.exp(np.log(np.sqrt(ron*roff))+1.5*np.log(ron/roff)*u-2*np.log(ron/roff)*u**3)

def main():
    folder=ROOT/'diagnostics';folder.mkdir(exist_ok=True)
    ng=NgSpice();report={'source':'https://raw.githubusercontent.com/imr/ngspice/master/src/xspice/icm/xtradev/pswitch/cfunc.mod','curves':[], 'dc_reference':[]}
    path=folder/'s2_curve.cir'
    path.write_text(f'''TI S2 port actual resistance curve diagnostic
.param V_out=3.3
.include "{TI}"
Vtest test 0 .001
Vcontrol control 0 0
XSW control 0 test 0 TPS7A20_ADJ_S2
.dc Vcontrol -10u 1.01m 10u
.end
''')
    ng.command('source '+str(path));ng.command('run')
    controls=ng.vector('v(control)');r=.001/(-ng.vector('i(vtest)'))
    original=switch_resistance(controls,1e6,1e-6)
    predicted=switch_resistance(controls,1e-6,1e6,True)
    for target in [0,.00025,.0005,.00075,.001]:
        i=int(np.argmin(abs(controls-target)))
        report['curves'].append({'control_v':float(controls[i]),'original_mathematical_ohm':float(original[i]),'ported_ngspice_measured_ohm':float(r[i]),'ported_ngspice_predicted_ohm':float(predicted[i])})
    report['ported_curve_relative_error_max']=float(np.max(abs(r-predicted)/predicted))
    print('curve check',report,flush=True)
    (folder/'s2_curve.log').write_text('\n'.join(ng.log)+'\n')
    np.savetxt(folder/'s2_curve.csv',np.column_stack([controls,original,predicted,r]),delimiter=',',header='control_v,original_pspice_math_ohm,ported_expected_ohm,ported_measured_ohm',comments='')
    for label,model,method in [('original_trap',TI_ORIGINAL,'trap'),('ported_trap',TI,'trap'),('ported_gear',TI,'gear')]:
        path=folder/(label+'.cir')
        path.write_text(f'''TI loaded reference, {label}
.param V_out=3.3
.include "{model}"
.options method={method} reltol=.001
Vsrc vin 0 PWL(0 0 1m 0 1.01m 5 12m 5)
XU vin 0 vin nc vout TPS7A20_ADJ_TRANS
Cin vin 0 4.7u
Cout vout 0 8u
Rload vout 0 55
.tran 1u 12m
.end
''')
        ng.log=[];ng.command('destroy all');ng.command('source '+str(path));ng.command('run')
        t=ng.vector('time');v=ng.vector('v(vout)')
        row={'name':label,'vout_last_v':float(v[-1]),'time_last_s':float(t[-1]),'sane':bool(3.2<v[-1]<3.4 and t[-1]>=.012-1e-9)}
        report['dc_reference'].append(row)
        (folder/(label+'.log')).write_text('\n'.join(ng.log)+'\n')
        assert row['sane'],row
    report['on_state_extra_drop_at150mA_v']=.15*(.001-1e-6)
    report['transition_error_note']='Ron lower clamp changes the nanosecond-scale intermediate resistance too; this is an explicit port approximation, not an exact PSpice equivalence.'
    (folder/'port_validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()

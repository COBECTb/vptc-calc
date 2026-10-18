"""Export native test schematics with KiCad and execute their exported SPICE decks."""
from pathlib import Path
import json,sys,subprocess,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'power'))
from run_power import NgSpice

def main():
    ng=NgSpice();ng.command('set ngbehavior=psa');out=ROOT/'kicad/exported';out.mkdir(exist_ok=True)
    baseline={q['case']:q for q in json.loads((ROOT/'power/results/summary.json').read_text())};rows=[]
    for sch in sorted((ROOT/'kicad').glob('*.kicad_sch')):
        deck=out/(sch.stem+'.cir')
        subprocess.run(['/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli','sch','export','netlist',str(sch),'--format','spice','-o',str(deck)],check=True,capture_output=True)
        assert 'X1 VSRC VIN VOUT REMOTE LOADCMD 0 ENCODER_V2_POWER_BENCH' in deck.read_text()
        ng.command('destroy all');ng.log=[];ng.command('source '+str(deck));ng.command('run')
        (out/(sch.stem+'.log')).write_text('\n'.join(ng.log)+'\n')
        data={s:ng.vector(s) for s in ['time','v(vin)','v(vout)','v(remote)']};t=data['time']
        complete=bool(t[-1]>=.012-1e-9 and not any('aborted' in q.lower() or 'timestep too small' in q.lower() for q in ng.log))
        ref=baseline[sch.stem];assert complete==ref['solver_complete'],sch.stem
        project=sch.with_suffix('.kicad_pro');settings=json.loads(project.read_text())
        assert settings['schematic']['ngspice']['model_mode']==2
        row={'case':sch.stem,'kicad_export_sha256':hashlib.sha256(deck.read_bytes()).hexdigest(),'solver_complete':complete,'simulation_end_ms':float(t[-1]*1e3),'schematic_sha256':hashlib.sha256(sch.read_bytes()).hexdigest(),'project_sha256':hashlib.sha256(project.read_bytes()).hexdigest()}
        if complete:
            event=(t>.0045)&(t<.010)
            for key,metric in [('remote_transient_min_v',np.min),('remote_transient_max_v',np.max)]:
                row[key]=float(metric(data['v(remote)'][event]));row[key+'_difference_from_direct_v']=abs(row[key]-ref[key]);assert abs(row[key]-ref[key])<.001,(sch.stem,key,row[key],ref[key])
        else:row['assessment']='Unresolved model convergence during interruption; no pass claimed.'
        rows.append(row);print(sch.stem,complete,flush=True)
    report={'method':'KiCad 10.0.7 native .kicad_sch -> KiCad SPICE exporter -> bundled ngspice 45.2, ngbehavior=psa, matching native PSpice compatibility mode 2; GUI not operated because Mac was locked.','results':rows}
    (ROOT/'kicad/native_verification.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':main()

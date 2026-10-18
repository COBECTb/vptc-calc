#!/usr/bin/env python3
"""Refine the most demanding in-range load step without overwriting its run."""
import json
import numpy as np
from run_power import ROOT, NgSpice, CASES, make_netlist, summarize, validate_model

case = next(c for c in CASES if c['name'] == 'load_30_to_150mA_derated')
baseline = next(r for r in json.loads((ROOT/'results/summary.json').read_text()) if r['case'] == case['name'])
path = ROOT/'netlists/load_step_refined_50ns.cir'
path.write_text(make_netlist(case).replace('.tran .2u .012 0 .2u', '.tran .05u .012 0 .05u'))
ng = NgSpice()
validate_model(ng)
data = ng.run(path)
assert ng.complete
refined = summarize(case, data)
changes = {name: abs(refined[name] - baseline[name]) for name in ('transient_min_v','transient_max_v','remote_transient_min_v','remote_transient_max_v')}
assert max(changes.values()) < .001, changes
result = {'baseline_step_ns':200, 'refined_step_ns':50, 'case':case['name'],
          'absolute_change_v':changes,'refined_metrics':refined,'pass_under_1mv':True}
(ROOT/'results/convergence.json').write_text(json.dumps(result,indent=2)+'\n')
(ROOT/'results/convergence.log').write_text('\n'.join(ng.log)+'\n')
np.savez_compressed(ROOT/'results/convergence_trace.npz', **data)
print(json.dumps(result,indent=2))

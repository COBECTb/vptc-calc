"""Independent pin/function and release checks against reviewed datasheet pinouts.

Run with KiCad Python. Expected package functions are transcribed from primary
sources, separately from electrical_spec.json and the custom schematic symbols.
This is not a model of oscillator startup, EMC, Hall accuracy or real assembly.
"""
import datetime
from pathlib import Path
import json,hashlib,math,re
import pcbnew as p
from schematic_sexpr import parse,get,nodes,pins
R=Path(__file__).resolve().parents[1];b=p.LoadBoard(str(R/'encoder_can_v2.kicad_pcb'));fps={f.GetReference():f for f in b.GetFootprints()}
sch=parse((R/'encoder_can_v2.kicad_sch').read_text());libs={s[1]:s for s in nodes(get(sch,'lib_symbols'),'symbol')};instances={next(q[2] for q in nodes(s,'property') if q[1]=='Reference'):s for s in nodes(sch,'symbol')}
spec=json.loads((R/'design/electrical_spec.json').read_text());cs={c['ref']:c for c in spec['components']};checks=[]
def check(name,condition,detail):
 assert condition,(name,detail)
 checks.append(dict(check=name,passed=True,detail=detail))

def xy(v):return [p.ToMM(v.x),p.ToMM(v.y)]

functions={
 'U1':dict(zip(map(str,range(1,34)),['VDD','PF0','PF1','PG10','PA0','PA1','PA2','PA3','PA4','PA5','PA6','PA7','PB0','VSSA','VDDA','VSS','VDD','PA8','PA9','PA10','PA11','PA12','PA13','PA14','PA15','PB3','PB4','PB5','PB6','PB7','PB8','VSS','VSS'])),
 'U2':dict(zip(map(str,range(1,7)),['SCL','GND','TEST','VCC','INT','SDA'])),
 'U3':dict(zip(map(str,range(1,7)),['SCL','GND','TEST','VCC','INT','SDA'])),
 'U4':dict(zip(map(str,range(1,9)),['TXD','GND','VCC','RXD','NC','CANL','CANH','NC'])),
 'U5':dict(zip(map(str,range(1,6)),['IN','GND','EN','NC','OUT']))}
for ref,expected in functions.items():
 lib=libs[get(instances[ref],'lib_id')[1]];actual={get(q,'number')[1]:get(q,'name')[1] for q in pins(lib)}
 norm=lambda s:re.sub('[^A-Z0-9]','',s.upper())
 check(ref+' package pin functions',set(actual)==set(expected) and all(norm(v) in norm(actual[n]) for n,v in expected.items()),dict(actual=actual,expected=expected))

# These are intended connections, independently checked by physical pad number.
required={
 'U1':{'1':'+3V3','2':'HSE_IN','3':'HSE_OUT','4':'NRST','5':'INT_INNER','6':'INT_OUTER','9':'LED_CMD','10':'LED_PHASE','14':'GND','15':'+3V3','16':'GND','17':'+3V3','18':'I2C2_SDA','19':'I2C2_SCL','21':'CAN_RX','22':'CAN_TX','23':'SWDIO','24':'SWCLK','25':'I2C1_SCL','30':'I2C1_SDA','31':'BOOT0','32':'GND','33':'GND'},
 'U2':{'1':'I2C1_SCL','2':'GND','3':'GND','4':'+3V3','5':'INT_INNER','6':'I2C1_SDA'},
 'U3':{'1':'I2C2_SCL','2':'GND','3':'GND','4':'+3V3','5':'INT_OUTER','6':'I2C2_SDA'},
 'U4':{'1':'CAN_TX','2':'GND','3':'+3V3','4':'CAN_RX','6':'CAN_L','7':'CAN_H'},
 'U5':{'1':'+5V','2':'GND','3':'+5V','5':'+3V3'},
 'D1':{'1':'CAN_H','2':'CAN_L','3':'GND'},'Y1':{'1':'HSE_IN','2':'GND','3':'HSE_OUT','4':'GND'},
 'J1':{'1':'+5V','2':'GND','3':'CAN_H','4':'CAN_L'},'J2':{'1':'+5V','2':'GND','3':'SWDIO','4':'SWCLK','5':'NRST'}}
for ref,expected in required.items():
 actual={q.GetNumber():q.GetNetname() for q in fps[ref].Pads() if q.GetNumber()}
 check(ref+' physical pad nets',all(actual[n]==net for n,net in expected.items()),expected)
for ref,numbers in [('U4',['5','8']),('U5',['4'])]:
 actual={q.GetNumber():q.GetNetname() for q in fps[ref].Pads()}
 check(ref+' NC pads',all(actual[n].startswith('unconnected-') for n in numbers),numbers)
check('Unchanged Hall footprints',all(cs[r]['mpn']=='TMAG5273A2QDBVR' for r in ['U2','U3']),{r:cs[r]['mpn'] for r in ['U2','U3']})
check('Exact crystal',cs['Y1']['mpn']=='ABM10-16.000MHZ-12-R80-3-D30-T' and all(cs[r]['value']=='18pF' for r in ['C13','C14']),dict(mpn=cs['Y1']['mpn'],load_caps_pf=18))
check('Optional CAN termination',cs['R9']['dnp'] and fps['R9'].IsDNP() and cs['R9']['value']=='120','Only two bus ends may be terminated')

bypass={r:c for r,c in [('C1','100nF'),('C2','100nF'),('C3','4.7uF'),('C4','10nF'),('C5','1uF'),('C6','100nF'),('C7','100nF'),('C8','100nF'),('C9','1uF'),('C10','4.7uF'),('C11','4.7uF'),('C12','100nF')]}
check('Bypass/reset capacitor values',all(cs[r]['value']==val for r,val in bypass.items()),bypass)
check('Supply and reset constraints',all(cs[r]['value']=='2.2k' for r in ['R1','R2','R3','R4']) and all(cs[r]['value']=='10k' for r in ['R5','R6','R7','R8']),dict(i2c_pullups_ohm=2200,reset_irq_boot_ohm=10000))

leds=[]
for ref in ['D2','D3','D4']:
 f=fps[ref];pads={q.GetNumber():q for q in f.Pads()};a,z=pads['1'],pads['2'];sizes=[xy(q.GetSize()) for q in [a,z]];pitch=math.dist(xy(a.GetPosition()),xy(z.GetPosition()))
 areas=[]
 for q in [a,z]:
  w,h=xy(q.GetSize());mx,my=xy(q.GetSolderPasteMargin(p.B_Cu));areas.append((w+2*mx)*(h+2*my)/(w*h))
 check(ref+' Kingbright lands',all(abs(sz[0]-.7)<1e-6 and abs(sz[1]-.5)<1e-6 for sz in sizes) and abs(pitch-.9)<2e-6 and all(abs(x-.8)<1e-4 for x in areas),dict(pad_size_mm=sizes,pitch_mm=pitch,paste_area_ratios=areas,cathode_net=a.GetNetname()))
 leds.append(dict(ref=ref,rotation_deg=f.GetOrientationDegrees(),position_mm=xy(f.GetPosition()),cathode_pad=1,anode_pad=2))
check('LED series resistors',all(cs[r]['value']=='1k' for r in ['R10','R11','R12']),dict(max_current_per_channel_at_zero_vf_ma=3.3495/990*1000,max_resistor_power_w=3.3495**2/990))
ep=next(q for q in fps['U1'].Pads() if q.GetNumber()=='33');windows=[q for q in fps['U1'].Pads() if not q.GetNumber() and q.IsOnLayer(p.B_Paste)]
window_sizes=[xy(q.GetSize()) for q in windows];paste_area=sum(w*h-(4-math.pi)*p.ToMM(q.GetRoundRectCornerRadius())**2 for q,(w,h) in zip(windows,window_sizes));ep_area=math.prod(xy(ep.GetSize()))
check('MCU thermal pad paste coverage',len(windows)==9 and all(abs(w-.9)<1e-6 and abs(h-.9)<1e-6 for w,h in window_sizes) and ep.GetNetname()=='GND' and .5<paste_area/ep_area<.8,dict(copper_mm2=ep_area,paste_mm2=paste_area,paste_windows=len(windows),coverage_ratio=paste_area/ep_area))
report=dict(date=datetime.date.today().isoformat(),source_pcb_sha256=hashlib.sha256((R/'encoder_can_v2.kicad_pcb').read_bytes()).hexdigest(),checks=checks,led_assembly=leds,derived=dict(logic_supply_with_1p5pct_tolerance_v=[3.3*.985,3.3*1.015],i2c_capacitance_budget_at_300ns_pf=.3e-6/(.8473*2200*1.01)*1e12,ldo_peak_dissipation_at_5p5V_150mA_w=(5.5-3.3)*.15),sources=['https://www.st.com/resource/en/datasheet/stm32g431kb.pdf','https://www.ti.com/lit/ds/symlink/tmag5273.pdf','https://www.ti.com/lit/ds/symlink/tcan332g.pdf','https://www.ti.com/lit/ds/symlink/tps7a20.pdf','https://assets.nexperia.com/documents/data-sheet/PESD5V0S2BT.pdf','https://www.kingbrightusa.com/images/catalog/SPEC/APG1005SYC-T.pdf'],limits=['Pin/function checks are based on reviewed primary documentation; not device simulation.','C13/C14 are initial load values; oscillator safety factor and drive level need hardware characterization.','64mA average is a planning estimate. Check actual power and thermals; 150mA is a qualification budget.','I2C bus capacitance, CAN immunity, power sequencing and magnetic accuracy are not measured here.'])
(R/'design/electrical_release_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('Independent electrical release checks:',len(checks),'passed')

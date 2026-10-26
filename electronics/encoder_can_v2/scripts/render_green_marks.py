from pathlib import Path
import json,hashlib,shutil
R=Path(__file__).resolve().parents[1];H=R/'design';V=R/'design';p=R/'scripts/render_views.py';g={'__file__':str(p)};exec(compile(p.read_text().split('in1_signals=')[0],str(p),'exec'),g);plt=g['plt'];after=g['d'];before=json.loads((H/'green_marks_before_geometry.json').read_text());assert after['source_pcb_sha256']==hashlib.sha256((R/'encoder_can_v2.kicad_pcb').read_bytes()).hexdigest()
regions=[('1 · R5 / BOOT0: убран острый возврат',(25.1,29.2,-8.1,-3.4),['R5']),('2 · C8: упрощён подвод питания',(19.8,23.8,5.9,10.3),['C8']),('3 · C4 / C5: общий ствол вместо обходов',(24.2,27.9,-3.85,2.8),['C4','C5'])]
fig,axes=plt.subplots(3,2,figsize=(12,14),constrained_layout=True)
for row,(name,bounds,refs) in enumerate(regions):
 for col,(data,label) in enumerate([(before,'До'),(after,'После')]):
  g['d']=data;ax=axes[row,col];g['draw'](ax,'F.Cu');ax.set(xlim=bounds[:2],ylim=bounds[2:],title=name+' · '+label,xlabel='',ylabel='');ax.set_xticks([]);ax.set_yticks([]);ax.grid(False)
  for p in data['pads']:
   if p['ref'] in refs and p['num']:
    ax.text(*g['local'](p['xy']),p['ref']+'.'+p['num']+'\n'+p['net'],ha='center',va='center',fontsize=7,bbox=dict(facecolor='white',alpha=.8,edgecolor='none',pad=.3),zorder=8)
fig.suptitle('Три последних зелёных правки внесены в PCB\nОдинаковые участки и масштаб · показана медь без маски',fontsize=14);dest=R/'design/green_marks_review.png';fig.savefig(dest,dpi=180);plt.close(fig)
g['d']=after;fig,axes=plt.subplots(1,2,figsize=(9,11),constrained_layout=True)
for ax,layer,title in zip(axes,['F.Cu','B.Cu'],['Передняя сторона · Hall / CAN / питание','Обратная сторона · MCU / кварц / LED']):
 g['draw'](ax,layer);ax.set_title(title,fontsize=11);ax.set_xlabel('мм');ax.set_ylabel('мм')
fig.suptitle('Актуальная разводка · три зелёные правки применены\nМаска скрыта для просмотра дорожек; переходы закрыты маской',fontsize=12);fig.savefig(V/'green_marks_front_back.png',dpi=190);plt.close(fig);print(dest)

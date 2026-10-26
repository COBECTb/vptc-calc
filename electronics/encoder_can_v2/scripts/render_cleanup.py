"""Matched close-ups of the same locations before and after route cleanup."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
code=(R/'scripts/render_views.py').read_text().split('fig,axs=plt.subplots(1,4')[0]
exec(compile(code,str(R/'scripts/render_views.py'),'exec'))
before=json.loads((R/'design/cleanup_before_geometry.json').read_text());after=json.loads((R/'design/review_geometry.json').read_text())
pages=[
 [('U2 / Hall inner','F.Cu',(21.5,26.7,-2.4,3.7)),('U4 / CAN','F.Cu',(20.7,26.3,5.9,12.1)),('D1 / TVS','F.Cu',(23.,28.,3.3,7.0))],
 [('U5 / supply','F.Cu',(19.5,27.,-12.7,-5.7)),('U1 / C1 right','B.Cu',(30.5,33.9,-5.,2.2)),('U1 / left exits','B.Cu',(22.7,28.,-4.,4.3))],
 [('Pullups / upper exits','B.Cu',(23.,32.8,2.5,8.1)),('Internal routes near H2','In2.Cu',(24.,33.8,6.8,13.)),('U1 / crystal region','B.Cu',(25.2,33.7,-9.5,-2.3))]
]
for index,regions in enumerate(pages,1):
 fig,axes=plt.subplots(3,2,figsize=(12,13),constrained_layout=True)
 for row,(name,layer,bounds) in enumerate(regions):
  for col,(data,label) in enumerate([(before,'До · V2.3'),(after,'После · V2.4')]):
   d=data;ax=axes[row,col];draw(ax,layer);ax.set(xlim=bounds[:2],ylim=bounds[2:],title=name+' · '+label);ax.set_xticks([]);ax.set_yticks([]);ax.set_xlabel('');ax.set_ylabel('')
 fig.suptitle('Одинаковые участки и масштаб · реальные дорожки платы\nЗдесь показана медь; открытые площадки — на mask_review.png',fontsize=13);fig.savefig(R/f'design/cleanup_details_{index}.png',dpi=180);plt.close(fig)

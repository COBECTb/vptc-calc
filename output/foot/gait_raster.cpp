// Small depth-buffer renderer for previews of the native OpenSCAD STL surfaces.
#include <algorithm>
#include <cmath>
#include <cstdint>
extern "C" void raster(int w,int h,int count,const float* tri,const float* rgb,
                       const float* basis,float scale,float cx,float cy,
                       uint8_t* out,float* depth) {
 for(int i=0;i<count;i++) {
  float p[3][3];
  for(int j=0;j<3;j++) {
   const float* v=tri+9*i+3*j;
   for(int a=0;a<3;a++) p[j][a]=v[0]*basis[3*a]+v[1]*basis[3*a+1]+v[2]*basis[3*a+2];
   p[j][0]=cx+scale*p[j][0];p[j][1]=cy-scale*p[j][1];
  }
  float area=(p[1][0]-p[0][0])*(p[2][1]-p[0][1])-(p[1][1]-p[0][1])*(p[2][0]-p[0][0]);
  if(std::abs(area)<1.e-7f)continue;
  int xmin=std::max(0,(int)std::floor(std::min({p[0][0],p[1][0],p[2][0]})));
  int xmax=std::min(w-1,(int)std::ceil(std::max({p[0][0],p[1][0],p[2][0]})));
  int ymin=std::max(0,(int)std::floor(std::min({p[0][1],p[1][1],p[2][1]})));
  int ymax=std::min(h-1,(int)std::ceil(std::max({p[0][1],p[1][1],p[2][1]})));
  const float *v=tri+9*i;
  float ax=v[3]-v[0],ay=v[4]-v[1],az=v[5]-v[2],bx=v[6]-v[0],by=v[7]-v[1],bz=v[8]-v[2];
  float nx=ay*bz-az*by,ny=az*bx-ax*bz,nz=ax*by-ay*bx,norm=std::sqrt(nx*nx+ny*ny+nz*nz);
  // Double-sided lighting also handles the original open imported mounting STLs.
  float light=norm>0 ? .58f+.42f*std::abs((-.35f*nx-.45f*ny+.82f*nz)/norm) : 1;
  for(int y=ymin;y<=ymax;y++)for(int x=xmin;x<=xmax;x++) {
   float xx=x+.5f,yy=y+.5f;
   float b=((xx-p[0][0])*(p[2][1]-p[0][1])-(yy-p[0][1])*(p[2][0]-p[0][0]))/area;
   float c=((p[1][0]-p[0][0])*(yy-p[0][1])-(p[1][1]-p[0][1])*(xx-p[0][0]))/area;
   if(b<-.00001f||c<-.00001f||b+c>1.00001f)continue;
   float z=p[0][2]+b*(p[1][2]-p[0][2])+c*(p[2][2]-p[0][2]);int k=y*w+x;
   if(z<=depth[k])continue;
   depth[k]=z;for(int ch=0;ch<3;ch++)out[3*k+ch]=(uint8_t)std::clamp(rgb[3*i+ch]*light,0.f,255.f);
  }
 }
}

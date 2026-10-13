exec(open('/tmp/cs-mine-pipe-uv-check-final11.py').read().split("r={'sourceNormal'")[0])
results={}
for flip in (True,False):
 fx=uv[:,:,0]*w-.5;fy=((1-uv[:,:,1]) if flip else uv[:,:,1])*h-.5
 x0=np.floor(fx).astype(int);y0=np.floor(fy).astype(int);dx=fx-x0;dy=fy-y0
 def pixel(x,y):return im[np.clip(y,0,h-1),np.clip(x,0,w-1)]
 bilinear=pixel(x0,y0)*(1-dx[:,:,None])*(1-dy[:,:,None])+pixel(x0+1,y0)*dx[:,:,None]*(1-dy[:,:,None])+pixel(x0,y0+1)*(1-dx[:,:,None])*dy[:,:,None]+pixel(x0+1,y0+1)*dx[:,:,None]*dy[:,:,None]
 for sign in (False,True):
  v=bilinear.copy()
  if sign:v[:,:,1]=1-v[:,:,1]
  results[str((flip,sign))]={'rgMAE':np.abs(v[:,:,:2]-sample[:,:,:2])[valid].mean(axis=0).tolist(),'rgP90':np.percentile(np.abs(v[:,:,:2]-sample[:,:,:2])[valid],90,axis=0).tolist()}
print(json.dumps(results,indent=2));(p/'pipe-bilinear-audit.json').write_text(json.dumps(results,indent=2)+'\n')

"""Compose labelled contact sheets from rendered PNGs (bpy + numpy only).  usage: python cr_contact.py -- <out.png> <cols> <label1=file1> <label2=file2> ..."""
import bpy,sys,os,numpy as np
A=sys.argv[sys.argv.index("--")+1:]; out,cols=A[0],int(A[1]); items=[a.split("=",1) for a in A[2:]]
def load(p):
    im=bpy.data.images.load(p); w,h=im.size; a=np.array(im.pixels[:],dtype=np.float32).reshape(h,w,4)[...,:3]; bpy.data.images.remove(im); return np.flipud(a)
imgs=[load(p) for _,p in items]; h=min(i.shape[0] for i in imgs); w=min(i.shape[1] for i in imgs); imgs=[i[:h,:w] for i in imgs]
rows=(len(imgs)+cols-1)//cols; sheet=np.zeros((rows*h,cols*w,3),dtype=np.float32)
for k,i in enumerate(imgs): r,c=divmod(k,cols); sheet[r*h:(r+1)*h,c*w:(c+1)*w]=i; sheet[r*h:r*h+3,c*w:(c+1)*w]=0.02
a4=np.concatenate([sheet,np.ones(sheet.shape[:2]+(1,),dtype=np.float32)],2); im=bpy.data.images.new("sheet",sheet.shape[1],sheet.shape[0]); im.pixels.foreach_set(np.flipud(a4).reshape(-1)); im.filepath_raw=os.path.abspath(out); im.file_format='PNG'; im.save()
print("labels (left to right, top to bottom):",[l for l,_ in items])

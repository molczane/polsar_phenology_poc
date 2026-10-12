"""Convert quad-pol NISAR GCOV covariance terms C3 into Pauli-basis T3.

C3 corresponds to k=[HH,HV,VV]; Pauli vector=[HH+VV,HH-VV,2*HV]/sqrt(2).
All six independent C3 terms are required; dual-pol GCOV is not sufficient.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np

TERMS=("HHHH","HHHV","HHVV","HVHV","HVVV","VVVV")
PAULI_TRANSFORM=np.array([[1,0,1],[1,0,-1],[0,2,0]],dtype=np.complex128)/np.sqrt(2)

def covariance_to_t3(hhhh,hhhv,hhvv,hvhv,hvvv,vvvv):
    v=[np.asarray(a) for a in (hhhh,hhhv,hhvv,hvhv,hvvv,vvvv)]
    shape=v[0].shape
    if any(a.shape!=shape for a in v): raise ValueError("Covariance term dimensions differ")
    c=np.zeros(shape+(3,3),dtype=np.complex128)
    c[...,0,0],c[...,0,1],c[...,0,2],c[...,1,1],c[...,1,2],c[...,2,2]=v
    c[...,1,0]=c[...,0,1].conj()
    c[...,2,0]=c[...,0,2].conj()
    c[...,2,1]=c[...,1,2].conj()
    p=PAULI_TRANSFORM
    t=np.einsum("ia,...ab,jb->...ij",p,c,p.conj(),optimize=True)
    return (t+t.conj().swapaxes(-1,-2))/2

def convert_file(source:Path,destination:Path,frequency:str="A",row:int=0,col:int=0,height:int=256,width:int=256):
    import h5py
    if min(row,col)<0 or min(height,width)<1: raise ValueError("Invalid crop window")
    gp=f"/science/LSAR/GCOV/grids/frequency{frequency}"
    with h5py.File(source,"r") as h5:
        if gp not in h5: raise KeyError(f"{gp} not found. Confirm L2 GCOV product.")
        g=h5[gp]
        missing=[k for k in TERMS if k not in g]
        if missing: raise ValueError("Not full-pol GCOV; missing covariance terms "+", ".join(missing))
        maxrow,maxcol=g["HHHH"].shape
        if row>=maxrow or col>=maxcol: raise ValueError("Window starts outside image")
        r=slice(row,min(row+height,maxrow)); c=slice(col,min(col+width,maxcol))
        v=[g[k][r,c] for k in TERMS]
    t=covariance_to_t3(*v)
    if not np.isfinite(t).all(): raise ValueError("Subset contains NaN/Inf; choose another window")
    destination.parent.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(destination,T3=t.astype(np.complex64),provenance=f"NISAR L2 GCOV {source.name}, {frequency}, row={row}, col={col}")
    print(f"Wrote {destination}, shape {t.shape}")
    return destination

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("source",type=Path)
    p.add_argument("--output",type=Path,default=Path("data/real_T3.npz"))
    p.add_argument("--frequency",choices=["A","B"],default="A")
    p.add_argument("--row",type=int,default=0)
    p.add_argument("--col",type=int,default=0)
    p.add_argument("--height",type=int,default=256)
    p.add_argument("--width",type=int,default=256)
    a=p.parse_args()
    convert_file(a.source,a.output,a.frequency,a.row,a.col,a.height,a.width)

if __name__=="__main__":main()

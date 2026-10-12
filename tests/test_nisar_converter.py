"""Offline mathematical and file-format tests for NISAR C3 -> T3."""
import sys
from pathlib import Path
import h5py
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.convert_nisar_gcov import PAULI_TRANSFORM,TERMS,covariance_to_t3,convert_file

def test_analytic_pauli_conversion():
    rng=np.random.default_rng(40)
    s=rng.normal(size=(5,6,3))+1j*rng.normal(size=(5,6,3))
    c=s[..., :,None]*s[...,None,:].conj()
    t=covariance_to_t3(c[...,0,0],c[...,0,1],c[...,0,2],c[...,1,1],c[...,1,2],c[...,2,2])
    p=np.einsum("ab,...b->...a",PAULI_TRANSFORM,s)
    expected=p[..., :,None]*p[...,None,:].conj()
    np.testing.assert_allclose(t,expected,atol=1e-13)

def test_quad_pol_gcov_extract(tmp_path):
    source=tmp_path/"synthetic_quad.h5"
    with h5py.File(source,"w") as h5:
        g=h5.create_group("/science/LSAR/GCOV/grids/frequencyA")
        for k in TERMS:
            value=1 if k in ("HHHH","HVHV","VVVV") else 0
            g.create_dataset(k,data=np.full((8,9),value,dtype=np.complex64))
    output=tmp_path/"out.npz"
    convert_file(source,output,row=1,col=2,height=3,width=4)
    with np.load(output) as npz:
        assert npz["T3"].shape==(3,4,3,3)
        np.testing.assert_allclose(npz["T3"][0,0],np.diag([1,1,2]),atol=1e-6)

def test_refuses_dual_pol_gcov(tmp_path):
    source=tmp_path/"synthetic_dual.h5"
    with h5py.File(source,"w") as h5:
        g=h5.create_group("/science/LSAR/GCOV/grids/frequencyA")
        g.create_dataset("HHHH",data=np.ones((4,4)))
        g.create_dataset("HVHV",data=np.ones((4,4)))
    with pytest.raises(ValueError,match="Not full-pol GCOV"):
        convert_file(source,tmp_path/"out.npz")

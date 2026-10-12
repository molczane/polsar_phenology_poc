"""End-to-end mocked download and real-format HDF5 conversion; no satellite data."""
from pathlib import Path
import sys
import shutil
import numpy as np
import h5py
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from pull_real_data import build_parser,run

def test_authenticated_fake_download_and_real_format_conversion(monkeypatch,tmp_path):
    filename="NISAR_L2_PR_GCOV_001_030_A_001_4000_QPNA_A_20260915T010000_X.h5"
    fixture=tmp_path/"fixture.h5"
    with h5py.File(fixture,"w") as h5:
        g=h5.create_group("science/LSAR/GCOV/grids/frequencyA")
        for term in ("HHHH","HHHV","HHVV","HVHV","HVVV","VVVV"):
            if term=="HHHH":a=np.full((12,14),3.)
            elif term=="HVHV":a=np.full((12,14),2.)
            elif term=="VVVV":a=np.full((12,14),1.)
            else:a=np.zeros((12,14),dtype=np.complex64)
            g.create_dataset(term,data=a)
    class Product:
        properties={"fileID":filename,"sizeMB":1}
        def get_urls(self):return ["https://example.test/"+filename]
    class Session:
        def auth_with_token(self,token):
            assert token=="TEST_NOT_REAL_TOKEN"
            return self
    class FakeResults(list):
        def download(self,path,session,processes):
            assert processes==1
            shutil.copy(fixture,Path(path)/filename)
    class ASF:
        ASFSession=Session
        ASFSearchResults=FakeResults
        def granule_search(self,names):
            assert names==[filename]
            return FakeResults([Product()])
    monkeypatch.setenv("EARTHDATA_TOKEN","TEST_NOT_REAL_TOKEN")
    args=build_parser().parse_args([
        "--granule",filename,"--download","--raw-dir",str(tmp_path/"raw"),
        "--output",str(tmp_path/"T3.npz"),"--height","8","--width","9"])
    result=run(args,ASF())
    assert result["status"]=="downloaded_and_converted"
    assert (tmp_path/"T3.provenance.json").is_file()
    with np.load(tmp_path/"T3.npz") as f:t=f["T3"]
    assert t.shape==(8,9,3,3)
    assert np.isfinite(t).all()
    assert np.allclose(t,t.conj().swapaxes(-1,-2))

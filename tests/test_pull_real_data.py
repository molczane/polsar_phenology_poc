"""Offline ASF metadata selection and safety tests."""
import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from pull_real_data import is_quad_pol,choose_quad_pol,build_search_kwargs,build_parser,prevent_oversize,run

class Product:
    def __init__(self,name,size=30):
        self.properties={"fileID":name,"sizeMB":size,"startTime":"2026-09-01"}
    def get_urls(self):return ["https://example.test/scene.h5"]

def test_full_pol_only_and_filename_conventions():
    assert is_quad_pol(Product("NISAR_L2_PR_GCOV_001_001_D_001_4000_QPNA_A_20260901T120000_X.h5"))
    assert is_quad_pol(Product("NISAR_L2_PR_GCOV_001_001_D_001_4000_QPQP_A_20260901T120000_X.h5"))
    assert not is_quad_pol(Product("NISAR_L2_PR_GCOV_001_001_D_001_4000_DVNA_A_20260901T120000_X.h5"))
    assert not is_quad_pol(Product("NISAR_L2_PR_GCOV_001_001_D_001_4000_DHDV_A_20260901T120000_X.h5"))

def test_quad_selection_and_size_limit():
    products=[Product("NISAR_L2_GCOV_DVNA_a.h5"),Product("NISAR_L2_GCOV_QPNA_b.h5",9000)]
    assert choose_quad_pol(products) is products[1]
    with pytest.raises(RuntimeError,match="exceeds"):prevent_oversize(products[1],5)
    with pytest.raises(RuntimeError,match="No quad-pol"):choose_quad_pol(products[:1])

def test_bbox_granule_query_validation_and_offline_catalog():
    parser=build_parser()
    args=parser.parse_args(["--bbox","19.8","49.8","20.4","50.2","--list-only"])
    assert build_search_kwargs(args)["dataset"]=="NISAR"
    class ASF:
        def search(self,**kwargs):
            assert kwargs["processingLevel"]=="GCOV"
            return [Product("NISAR_L2_GCOV_DVNA_no.h5")]
    assert run(args,ASF())["status"]=="catalog_only"
    invalid=parser.parse_args(["--bbox","19.8","49.8","20.4","50.2"])
    with pytest.raises(ValueError,match="Choose --list-only"):run(invalid,ASF())
    with pytest.raises(ValueError,match="Supply --bbox"):
        build_search_kwargs(parser.parse_args(["--list-only"]))

def test_download_requires_full_pol_before_authentication():
    parser=build_parser()
    args=parser.parse_args(["--granule","NISAR_L2_GCOV_DVNA_fake","--download"])
    class ASF:
        def granule_search(self,names):return [Product("NISAR_L2_GCOV_DVNA_fake.h5")]
    with pytest.raises(RuntimeError,match="No quad-pol"):run(args,ASF())

from pathlib import Path
import sys
import pytest
import nbformat
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from run_real_notebook import inject_real_path

def test_injects_only_runtime_copy():
    nb=nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell("REAL_T3_PATH = None\nprint(REAL_T3_PATH)")])
    result=inject_real_path(nb,Path("data/real_T3.npz"))
    assert "REAL_T3_PATH = None" not in result.cells[0].source
    assert "real_T3.npz" in result.cells[0].source

def test_fails_when_notebook_config_missing():
    nb=nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell("print(42)")])
    with pytest.raises(ValueError,match="exactly one"):
        inject_real_path(nb,Path("data/real_T3.npz"))

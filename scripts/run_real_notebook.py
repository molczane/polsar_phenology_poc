"""Execute the existing notebook against a real T3 without editing its source."""
from __future__ import annotations
import argparse
from pathlib import Path
import nbformat
from nbclient import NotebookClient

def inject_real_path(nb,filepath:Path):
    marker="REAL_T3_PATH = None"
    replacement="REAL_T3_PATH = "+repr(str(filepath.resolve()))
    found=0
    for cell in nb.cells:
        if cell.cell_type=="code" and marker in cell.source:
            cell.source=cell.source.replace(marker,replacement,1)
            found+=1
    if found!=1: raise ValueError(f"Expected exactly one REAL_T3_PATH config cell; found {found}")
    return nb

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input",type=Path,default=Path("data/real_T3.npz"))
    p.add_argument("--notebook",type=Path,default=Path("01_polsar_decomposition_classification.ipynb"))
    p.add_argument("--output",type=Path,default=Path("executed-real-notebook.ipynb"))
    p.add_argument("--timeout",type=int,default=600)
    a=p.parse_args()
    if not a.input.is_file():raise FileNotFoundError(a.input)
    nb=inject_real_path(nbformat.read(a.notebook,as_version=4),a.input)
    result=NotebookClient(nb,timeout=a.timeout,kernel_name="python3").execute()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    nbformat.write(result,a.output)
    expected=Path("figures/06_real_scene_unlabeled_clusters.png")
    if not expected.is_file():raise FileNotFoundError(f"Expected result {expected} not generated")
    print(f"Executed real-data notebook: {a.output}")

if __name__=="__main__":main()

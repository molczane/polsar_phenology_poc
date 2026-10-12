"""Discover/download NISAR L2 GCOV quad-pol data and export a real T3 subset.

Use --list-only for public metadata. --download needs private Earthdata credentials;
raw scenes may be multi-GB. No fallback to synthetic data is permitted.
"""
from __future__ import annotations
import argparse
import json
import os
import re
from pathlib import Path
from typing import Any
from search_asf_catalog import bbox_wkt
from convert_nisar_gcov import convert_file

def is_quad_pol(product:Any)->bool:
    name=str(product.properties.get("fileID") or product.properties.get("sceneName") or "")
    return bool(re.search(r"(?:^|_)QP(?:NA|QP)?(?:_|\.)",name.upper()))

def summarize(product:Any)->dict:
    p=product.properties
    return {"id":p.get("fileID") or p.get("sceneName"),"quad_pol_filename":is_quad_pol(product),
            "start_time":p.get("startTime"),"polarization":p.get("polarization"),
            "size_mb":p.get("sizeMB"),"urls":product.get_urls()}

def get_session(asf:Any):
    token=os.environ.get("EARTHDATA_TOKEN")
    username=os.environ.get("EARTHDATA_USERNAME")
    password=os.environ.get("EARTHDATA_PASSWORD")
    if token:return asf.ASFSession().auth_with_token(token)
    if username and password:return asf.ASFSession().auth_with_creds(username,password)
    if (Path.home()/".netrc").exists():return asf.ASFSession()
    raise RuntimeError("NASA Earthdata authentication required: use EARTHDATA_TOKEN, "
                       "EARTHDATA_USERNAME/EARTHDATA_PASSWORD, or ~/.netrc. Never commit secrets.")

def build_search_kwargs(args:argparse.Namespace)->dict:
    if args.granule:return {"granule":args.granule}
    if args.bbox is None:raise ValueError("Supply --bbox W S E N or --granule EXACT_GRANULE_NAME.")
    q=dict(dataset="NISAR",processingLevel="GCOV",intersectsWith=bbox_wkt(args.bbox),
           start=args.start,end=args.end,maxResults=args.max_results)
    if args.maturity:q["dataMaturity"]=args.maturity
    return q

def search_products(asf:Any,query:dict):
    if "granule" in query:return asf.granule_search([query["granule"]])
    return asf.search(**query)

def choose_quad_pol(results:Any,index:int=0):
    products=[p for p in results if is_quad_pol(p)]
    if not products:raise RuntimeError(
        "No quad-pol (_QPNA_ or _QPQP_) NISAR GCOV. Broaden search or "
        "use an exact --granule. Dual-pol VV/VH is unsuitable for full T3.")
    if not (0<=index<len(products)):raise IndexError(f"--quad-index out of range, found {len(products)}")
    return products[index]

def prevent_oversize(product:Any,max_gb:float):
    size_mb=product.properties.get("sizeMB")
    if size_mb is not None and float(size_mb)/1024>max_gb:
        raise RuntimeError(f"Granule ~{float(size_mb)/1024:.2f} GiB exceeds --max-download-gb {max_gb}")

def build_parser()->argparse.ArgumentParser:
    p=argparse.ArgumentParser(description=__doc__)
    a=p.add_argument
    a("--bbox",type=float,nargs=4,metavar=("WEST","SOUTH","EAST","NORTH"))
    a("--granule",help="Exact NISAR GCOV scene/granule name")
    a("--start",default="2026-07-01")
    a("--end",default="2026-10-12")
    a("--maturity",choices=["PROVISIONAL","BETA"])
    a("--max-results",type=int,default=100)
    a("--quad-index",type=int,default=0)
    a("--list-only",action="store_true")
    a("--download",action="store_true")
    a("--max-download-gb",type=float,default=8)
    a("--raw-dir",type=Path,default=Path("data/raw"))
    a("--output",type=Path,default=Path("data/real_T3.npz"))
    a("--row",type=int,default=0)
    a("--col",type=int,default=0)
    a("--height",type=int,default=300)
    a("--width",type=int,default=400)
    a("--frequency",choices=["A","B"],default="A")
    return p

def run(args:argparse.Namespace,asf:Any):
    if args.max_results<=0 or args.max_download_gb<=0:
        raise ValueError("Limits must be positive.")
    if args.granule and args.bbox:raise ValueError("--granule and --bbox are mutually exclusive.")
    if not args.list_only and not args.download:
        raise ValueError("Choose --list-only or --download.")
    query=build_search_kwargs(args)
    results=search_products(asf,query)
    records=[summarize(p) for p in results]
    print(json.dumps({"query":query,"matched":len(records),"products":records},indent=2,default=str))
    if args.list_only:return {"status":"catalog_only","count":len(records)}
    product=choose_quad_pol(results,args.quad_index)
    prevent_oversize(product,args.max_download_gb)
    session=get_session(asf)
    args.raw_dir.mkdir(parents=True,exist_ok=True)
    asf.ASFSearchResults([product]).download(path=str(args.raw_dir),session=session,processes=1)
    filename=str(product.properties.get("fileID") or "")
    downloaded=args.raw_dir/Path(filename).name
    if not downloaded.is_file() or downloaded.suffix.lower() not in {".h5",".hdf5"}:
        raise FileNotFoundError(f"Downloaded HDF5 not found at {downloaded}; verify ASF metadata.")
    convert_file(downloaded,args.output,frequency=args.frequency,row=args.row,
                 col=args.col,height=args.height,width=args.width)
    manifest={"source":"NASA ASF NISAR L2 GCOV","scene":summarize(product),
              "full_polarimetric":True,"raw_file":str(downloaded),
              "converted_t3":str(args.output),
              "window":{"row":args.row,"col":args.col,"height":args.height,"width":args.width},
              "note":"Unsupervised real-data clusters are NOT validated land-cover classes."}
    provenance=args.output.with_suffix(".provenance.json")
    provenance.write_text(json.dumps(manifest,indent=2,default=str)+"\n")
    print(f"Real T3 ready: {args.output}; provenance: {provenance}")
    return {"status":"downloaded_and_converted","t3":str(args.output)}

def main():
    args=build_parser().parse_args()
    import asf_search as asf
    run(args,asf)

if __name__=="__main__":main()

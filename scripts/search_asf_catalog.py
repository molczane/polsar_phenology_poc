"""Search public ASF metadata for SAR acquisitions (no download)."""
import argparse
import json
from pathlib import Path

def bbox_wkt(bbox):
    w,s,e,n=bbox
    if not (-180<=w<e<=180 and -90<=s<n<=90):
        raise ValueError("Invalid bbox: expected west south east north in WGS84")
    return f"POLYGON(({w} {s},{e} {s},{e} {n},{w} {n},{w} {s}))"

def build_query(dataset,level,bbox,start,end,max_results,maturity):
    q=dict(dataset=dataset,processingLevel=level,intersectsWith=bbox_wkt(bbox),start=start,end=end,maxResults=max_results)
    if dataset=="NISAR" and maturity: q["dataMaturity"]=maturity
    return q

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dataset",choices=["NISAR","SENTINEL-1","ALOS PALSAR","UAVSAR"],default="NISAR")
    p.add_argument("--level",default="GCOV")
    p.add_argument("--bbox",type=float,nargs=4,required=True,metavar=("WEST","SOUTH","EAST","NORTH"))
    p.add_argument("--start",default="2026-07-01")
    p.add_argument("--end",default="2026-10-12")
    p.add_argument("--maturity",choices=["PROVISIONAL","BETA"])
    p.add_argument("--max-results",type=int,default=10)
    p.add_argument("--output",type=Path,default=Path("data/asf_search_results.json"))
    a=p.parse_args()
    import asf_search as asf
    q=build_query(a.dataset,a.level,a.bbox,a.start,a.end,a.max_results,a.maturity)
    records=[]
    for x in asf.search(**q):
        props=dict(x.properties)
        records.append(dict(id=props.get("fileID") or props.get("sceneName"),polarization=props.get("polarization"),startTime=props.get("startTime"),url=x.get_urls(),properties=props))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps({"query":q,"count":len(records),"items":records},indent=2,default=str))
    print(f"Found {len(records)} products; saved {a.output}")
    if a.dataset=="NISAR": print("Verify full-pol covariance terms before T3 decomposition.")

if __name__=="__main__": main()

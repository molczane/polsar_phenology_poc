# Real-data pipeline — NASA NISAR L2 GCOV

This project adds a reproducible **real satellite data input**, in addition to
the existing synthetic demo. It can search NASA ASF's NISAR catalogue, download
an authenticated full-polarimetric L-band GCOV HDF5, convert its covariance
channels into T3, and run the existing notebook. Real-data outputs are
**unlabeled scattering clusters**, not validated land-cover classes or BBCH
phenological stages.

## Install

~~~bash
python -m pip install -r requirements-real-data.txt
~~~

## 1. Find acquisitions

Search a location/date window without credentials:

~~~bash
python scripts/pull_real_data.py \
  --bbox 19.5 49.8 20.4 50.3 \
  --start 2026-07-01 --end 2026-10-12 \
  --max-results 100 --list-only
~~~

Quad-pol NISAR acquisitions are geographically restricted: a search near
Kraków may contain **no** suitable full-pol data. This is expected, not an
error. In that case find a quad-pol GCOV product with [ASF Vertex](
https://search.asf.alaska.edu/) in another region. The script selects filenames
with a _QPNA_ or _QPQP_ acquisition code; the converter also independently
validates that six C3 covariance terms really exist.

## 2. Download and convert

Obtain a free [NASA Earthdata Login](https://urs.earthdata.nasa.gov/).
Set a private EARTHDATA_TOKEN in your terminal environment or use .netrc.
Never commit credentials or include them in notebooks.

~~~bash
python scripts/pull_real_data.py \
  --granule 'EXACT_QUAD_POL_GCOV_SCENE_ID' \
  --download --max-download-gb 8 \
  --row 0 --col 0 --height 300 --width 400
~~~

The raw HDF5 is placed under git-ignored data/raw/ and converted into
data/real_T3.npz, with data/real_T3.provenance.json recording the source ID.
The converter requires HHHH, HHHV, HHVV, HVHV, HVVV and VVVV. It explicitly
rejects standard dual-pol VV/VH GCOV. Some tiles may contain invalid pixels;
choose another row/column if you encounter a nonfinite subset. The size
guard only works when ASF provides scene-size metadata; inspect disk space.

## 3. Run the existing notebook

~~~bash
python scripts/run_real_notebook.py --input data/real_T3.npz
~~~

This does not modify the original notebook. It writes
executed-real-notebook.ipynb and
figures/06_real_scene_unlabeled_clusters.png. Synthetic baseline metrics
remain explicitly synthetic; no real-data classification accuracy is asserted.

## 4. GitHub Actions

Select **Actions → Real data — ASF NISAR → Run workflow** on a branch
containing the workflow. Provide a NISAR GCOV granule ID.

- Default: catalogue-only metadata search (no download).
- For real download: create the Actions repository secret EARTHDATA_TOKEN;
  set the **download** input to true.
- Large scenes may exceed hosted runner disk, bandwidth, or runtime; prefer
  running on a local workstation for heavy datasets.
- Actions uploads only small derived results, never raw scene files.

## Scientific caveats

- Full-pol T3 requires full quad-pol covariance terms; dual-pol Sentinel-1
  cannot substitute.
- Covariance decomposition does not directly establish ground-truth land cover.
- For validated classification, obtain independent reference labels.
- The integration tests use synthetic HDF5 fixtures and mocked ASF downloads.
  A successful real NASA scene download/processing has NOT been verified yet.
- Record scene/granule identifiers, acquisition settings, processing level,
  source, access date, and appropriate attribution for research results.

Official documentation: [ASF Search](https://docs.asf.alaska.edu/asf_search/basics/),
[NISAR GCOV](https://nisar-docs.asf.alaska.edu/gcov/).

# Candidate SAR/PolSAR data sources

This page distinguishes **real SAR intensity**, **dual-pol coherent SAR**,
and **full quad-pol SAR** inputs for the crop phenology research pipeline.

| Provider | Sensor / product | Polarization and band | Recommended role |
|---|---|---|---|
| NASA ASF | NISAR L2 GCOV | L-band, dual- or quad-pol depending on acquisition | First automated full-pol C3-to-T3 pipeline when QP scene exists |
| NASA/JPL | UAVSAR | Fully polarimetric L-band airborne SAR | Agricultural field demonstration and decomposition |
| ESA/Copernicus | Sentinel-1 SLC | C-band dual-pol VV/VH or HH/HV depending on region/mode | Dense agricultural time series, dual-pol-specific pipeline |
| Canadian Space Agency / sample tutorials | RADARSAT-2 quad-pol | C-band full quad-pol | Full-pol land-cover decomposition demonstration |
| JAXA/ASF | ALOS PALSAR / PALSAR-2 | L-band; quad-pol availability depends on mode and access | Historic and cross-sensor comparisons |

## NISAR

- [ASF Vertex catalogue](https://search.asf.alaska.edu/)
- [ASF API and download examples](https://docs.asf.alaska.edu/asf_search/basics/)
- [NISAR product documentation](https://nisar-docs.asf.alaska.edu/gcov/)
- Geocoded covariance products are HDF5. The converter in this repo needs
  all six distinct full-pol C3 terms in an appropriate GCOV frequency group.
- Do not assume quad-pol over Poland; first inspect actual acquired scenes.
- NASA Earthdata authentication is needed for actual scene downloads.

## UAVSAR

- [JPL UAVSAR catalogue](https://uavsar.jpl.nasa.gov/cgi-bin/data.pl)
- [SMAPVEX12 agricultural campaign](https://uavsar.jpl.nasa.gov/cgi-bin/deployment.pl?id=L20120614)
- A good next-stage research source because fields and vegetation are the
  direct phenomena of interest. Requires a *separate* data adapter. The
  NISAR GCOV converter is **not** a UAVSAR reader.

## Sentinel-1

- [Copernicus Data Space](https://dataspace.copernicus.eu/)
- SLC is valuable for temporal VV/VH phase-sensitive features, but typical
  VV/VH SLC is **dual-polarization**, and standard GRD provides intensities,
  not the complex full scattering matrix.
- Implement a separate dual-pol analysis rather than manufacturing T3 data
  from VV/VH acquisitions.

## RADARSAT-2 and ALOS

- [ESA polarimetry tutorial](https://step.esa.int/docs/tutorials/S1TBX%20Polarimetry%20with%20Radarsat-2%20Tutorial_v2.pdf)
- [San Francisco PolSAR sample](https://ietr-lab.univ-rennes1.fr/polsarpro-bio/san-francisco/)
- [ASF ALOS reference](https://asf.alaska.edu/data-sets/sar-data-sets/alos-palsar/)
- Both can be valuable for interpreting surface/volume/double-bounce.
  Check exact product mode, rights, pricing and calibration.

## Evaluation principle

Synthetic H/A/alpha classification scores must never be reported as measured
accuracy on satellite imagery. A full-pol scattering-cluster map remains an
**unsupervised feature-space segmentation** until independently labeled and
validated against land-cover reference observations. Crop phenological stage
retrieval needs field-level stage labels and temporal observations.

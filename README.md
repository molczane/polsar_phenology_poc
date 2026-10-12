# Full-PolSAR Decomposition and Land-Cover Classification — Proof of Concept

Reproducible Jupyter notebook for a preliminary master's thesis demonstration requested by a supervisor: **can polarimetric decomposition features support land-cover classification?**

## 1. Run in minutes (no external dataset needed)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
jupyter notebook 01_polsar_decomposition_classification.ipynb
```

Use **Kernel → Restart & Run All**. The default experiment generates physically motivated **synthetic full-polarimetric sample coherency matrices** using complex Gaussian multi-look sampling, computes Cloude–Pottier **H / A / alpha** plus normalized Pauli powers, compares a backscatter/span-only Random Forest baseline with a polarimetric-features Random Forest, and evaluates on a **second independently simulated scene**. PNG figures and `figures/experiment_report.json` are written automatically.

## 2. What is / is not demonstrated

- **Demonstrated:** extraction of physically interpretable full-PolSAR descriptors from $T_3$; an end-to-end reproducible processing, plotting, classification and metric-export workflow.
- **Not demonstrated:** empirical land-cover classification accuracy, real SAR model validity, crop phenological stage or BBCH estimation.
- **Synthetic labels:** water-like, vegetation-like, built-up-like scattering *archetypes* only. The classes are defined by their simulated scattering statistics. Metrics cannot be generalized beyond the synthetic experiment.
- **The demonstration uses Cloude–Pottier H/A/alpha**, not Freeman–Durden decomposition. Normalized Pauli-channel powers are separate features, not equivalent to model-based surface/volume/double-bounce powers.

## 3. Use real quad-pol data (optional)

The notebook supports `(rows,cols,3,3)` complex `T3` saved to `data/real_T3.npz` with array key `T3` **or** a standard PolSARpro T3 folder containing `T11.bin`, `T22.bin`, `T33.bin`, `T12_real.bin`, `T12_imag.bin`, `T13_real.bin`, `T13_imag.bin`, `T23_real.bin`, `T23_imag.bin` and `T11.hdr` (ENVI float32 BSQ). It reads only a configurable small subset to keep memory low. Change `REAL_T3_PATH` in Section 5.

The optional real-image section generates **unlabeled K-means polarimetric clusters**, not ground-truth land-cover classes. To claim classification accuracy, collect independent reference labels and evaluate spatially disjoint held-out areas.

Suggested real source: ESA's [RADARSAT-2 full-PolSAR tutorial](https://step.esa.int/docs/tutorials/S1TBX%20Polarimetry%20with%20Radarsat-2%20Tutorial_v2.pdf) and its sample data; for production processing see [PyPolSARpro](https://polsarpro.readthedocs.io/en/latest/) or [PolSARtools](https://github.com/polsartools/polsartools).

**Note:** standard Sentinel-1 VV/VH dual-pol data do **not** contain the complete full-polarimetric T3 coherency matrix.

## 4. Repository structure

```text
01_polsar_decomposition_classification.ipynb
README.md
requirements.txt
figures/                            # produced by running notebook
  01_synthetic_inputs.png
  02_decomposition_features.png
  03_classification_comparison.png
  04_synthetic_confusion_matrices.png
  05_h_alpha_scatter.png
  experiment_report.json
data/                               # gitignored except .gitkeep
```

## 5. Next scientific steps

Replace synthetic toy observations with calibrated full-pol agricultural imagery, gather ground-truth land-cover polygons, and only then investigate time-series PolSAR signatures against crop BBCH observations. Evaluate across **held-out fields and seasons** and distinguish land-cover classification from phenological stage estimation.

## Scientific references

- Cloude & Pottier (1997), [DOI 10.1109/36.551935](https://doi.org/10.1109/36.551935).
- Freeman & Durden (1998), [DOI 10.1109/36.673687](https://doi.org/10.1109/36.673687).
- [ESA RADARSAT-2 Polarimetry Tutorial](https://step.esa.int/docs/tutorials/S1TBX%20Polarimetry%20with%20Radarsat-2%20Tutorial_v2.pdf).

## 6. GitHub Actions automation

The repository includes `.github/workflows/notebook-validation.yml`. On pushes to `main`, relevant pull requests, or **Actions → PolSAR notebook validation → Run workflow**, GitHub automatically:

1. Sets up Python and dependencies.
2. Executes the complete **synthetic** notebook in a fresh environment.
3. Verifies that all five figures and the provenance report exist.
4. Uploads the executed notebook, plots and report as a downloadable Actions artifact.

The workflow does **not** run a real-data experiment or download proprietary SAR imagery. Real-data acquisition and ground-truth validation must be added separately.

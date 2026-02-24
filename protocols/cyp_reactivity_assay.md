# CYP Reactivity Screening Assay Protocol

**Assay type:** CYP reactivity (SCIEX Echo MS+ ZenoTOF 7600)
**Enzymes:** CYP3A4, CYP2J2
**Reagents:** DLS Gentest Supersomes (+CPR+b5)

- CYP3A4: Cat. 456202, Lot 2408083
- CYP2J2: Cat. 456264, Lot 2211291

**Internal Regeneration System (IRS)** — prepared in 100 mM KPO4, pH 8:

- Glucose-6-phosphate disodium salt (G6P-Na2): 0.333 M (MW 304.098 g/mol)
- Glucose-6-phosphate dehydrogenase (G6PD): 30 U/mL (ThermoFisher, Cat. J61181-4I)

## Assay Parameters

| Parameter               | Value                       |
| ----------------------- | --------------------------- |
| Enzyme concentration    | 50 nM                       |
| Substrate concentration | 5 uM                        |
| Reaction volume         | 2 uL                        |
| Incubation              | 2 hrs @ 37C (no shaking)    |
| Plate format            | 1536-well (Labcyte LP-0400) |

## Experimental Design

- Two experimental conditions per compound: +/- CYP activity (controlled by omission of NADPH regeneration system)
- Experimental condition: CYP enzyme + buffer + NADPH regeneration system
- Control condition: CYP enzyme + buffer - NADPH regeneration system
- 4 replicates per condition in the experimental (+NADPH) plates
- Negative control wells (-NADPH) are pooled (7 compounds per well) since only TOF-MS (MS1) quantification is used, reducing total plates from 14 to 8 (4 per CYP isoform)
- 10 wells reserved for control substrates (midazolam/albendazole) per plate
- 8 wells -NADP, 8 wells +NADP for controls
- Assay buffer: 10 mM KPO4, pH 8 + 10 mM MgCl2

## Protocol

### Day 0: ARP Design and Generation

#### Intermediate dilution plate preparation

1. Design ARP layout.
   - To keep final DMSO % low, only a single 2.5 nL droplet is dispensed from the Echo (~0.12% of 2 uL assay volume). This requires making intermediate dilution plates at 4 mM to achieve the final target of 5 uM.
2. Generate the intermediate dilution plate (single 1536-well plate) using the Beckman Coulter Echo 655.

#### Dispensing compounds into assay plates

1. Use the Beckman Coulter Echo 655 acoustic liquid handler to print compounds from the intermediate plate into assay-ready plates (ARPs).

### Day 1: CYP3A4/CYP2J2 Reactivity Assay

**Equipment:** Agilent BioTek MultiFlo with Steinle 1 uL ruby metal tip cassettes (Cat. ST-2170009) for all liquid dispenses. Use fast dispense speed to mitigate beading.

1. **Prepare CYP master mix.**

2. **Assign MultiFlo dispense lines:**
   - Pin 1 (topmost): -regen / -NADP (control)
   - Pins 2-8: +regen / +NADP (experimental)

3. **Dispense CYP master mix** (both - and + regen conditions):
   - Prime 1x, then dispense 1 uL into each well.
   - Seal plates with Polar seal.
   - Spin 500g x 30 sec.
   - Incubate at RT for 15 min.

4. **Dispense NADP solution** (or buffer only for Pin 1 / control condition):
   - Prime 2x then dispense 1 uL into each well.

5. **Incubate:**
   - Seal plates, spin 500g x 30 sec.
   - Incubate at 37C for 2 hrs (no shaking).

6. **Quench reaction:**
   - Using dedicated 1 uL DMSO cassette: prime 2x, pre-dispense 400 uL, then dispense 5 uL of DMSO + 0.14% formic acid.
   - Final volume: 7 uL (final 0.1% formic acid).

7. **Store:**
   - Spin plates 500g x 1 min.
   - Store at -25C.

### Day 2: Running Plates on SCIEX Echo MS+ ZenoTOF 7600

1. **Thaw plates:** Collect plates from -25C freezer and thaw at room temp for 30 min (4 plates at a time).

2. **Prepare plates:**
   - Spin plates 500g x 30 sec.
   - Shake plates on orbital shaker at 1350 RPM x 1 min.

3. **Equilibrate SCIEX Echo MS+:**
   - **Carrier solvent:** 5 mM ammonium formate in 10% MeOH / 80% ACN / 10% H2O, flow rate 460 uL/min.
   - **MS settings (positive mode, TOF-MS1 only):** spray voltage 5000 V, mass range 80-1000 Da, accumulation time 0.1 sec.
   - Prior to first plate of each run:
     - Equilibrate MS method for 10 min. Run SCIEX OS Positive mode quick check; apply settings.
     - Equilibrate MS method alongside carrier solvent flow for 15 min.

4. **Acquire data:**
   - Run assay plates (10 nL ejections, 2.5 sec ejection interval).
   - Between runs, run a 5 min Echo-MS+ wash protocol (wash buffer: 50:50 water:methanol).

### Analysis

1. **Raw data splitting:** SCIEX OS software splits raw `.wiff` files into per-well data, then synced to AWS S3.
2. **Parquet conversion:** Command-line parsing tools (using SCIEX Data API) convert split data into four parquet tables: samples (well metadata), scans (retention time, TIC), scan_types (MS scan metadata), and spectra (raw m/z and intensity values).
3. **Mass calculation:** For each compound, exact monoisotopic mass is calculated from SMILES, then the [M+H]+ adduct mass is computed.
4. **XIC extraction and peak area integration:** Parquet files are loaded into an in-memory DuckDB database for efficient querying. Extracted ion chromatograms (XICs) are pulled at target m/z +/- 10 ppm tolerance, and peak areas are calculated by integrating ion intensity across the ejection time window.
5. **Reactivity quantification:** For each compound, peak areas in the experimental (+NADPH) condition are compared to the control (-NADPH) condition to quantify CYP-dependent substrate depletion.

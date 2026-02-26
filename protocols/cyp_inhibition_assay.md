# CYP3A4 Inhibition Assay Protocol (Active Preincubation)

**Assay:** C3A4IAP — CYP3A4 Inhibition, Active Preincubation
**Plate format:** 1536-well (Revvity Black CulturPlate, Cat. 6004660)

> **Active preincubation** means the enzyme is active during the preincubation phase — compound is preincubated with CYP enzyme, NADP+, and the regeneration system. This is distinct from "inactive preincubation" (C3A4IIP) where the enzyme is not active during preincubation.

## Assay Parameters

Compounds were tested in 12-point dose-response curves ranging from ~0.1 nM to ~50 uM (~3-fold serial dilutions).

| Parameter                          | Value                                           |
| ---------------------------------- | ----------------------------------------------- |
| Compound concentration range       | ~0.1 nM – 50 uM (12-point, ~3-fold dilutions)  |
| CYP3A4 concentration               | 5 nM (in assay)                                 |
| NADP+ concentration                | 100 uM (in assay)                               |
| Internal regeneration system (IRS) | 1X (in assay)                                   |
| Substrate (DBOMF)                  | 2 uM (in assay)                                 |
| Reaction buffer                    | 100 mM KPO4, pH 8                               |
| CYP enzyme master mix volume       | 2 uL/well                                       |
| Substrate master mix volume        | 2 uL/well                                       |
| Stop buffer volume                 | 2 uL/well                                       |
| Total assay volume                 | 6 uL/well                                       |
| Preincubation                      | 30 min at RT                                    |
| Substrate reaction                 | 30 min at 25C                                   |
| Stop buffer                        | 0.5 M Tris                                      |
| Readout                            | Fluorescence (Molecular Devices SpectraMax i3x) |

## Protocol

### 1. Prepare CYP Enzyme Master Mix

Combine CYP3A4 supersome, NADP+, internal regeneration system, and reaction buffer.

1. Obtain 1X Reaction Buffer (100 mM KPO4, pH 8).
2. Obtain CYP3A4 Supersome vials (DLS Gentest, Cat. 456202, Lot 2408083). Allow to come to RT and thaw before opening.
3. Obtain NADP+ (10 mM NADP+ in 100 mM KPO4, pH 8 buffer). Allow to come to RT before opening.
4. Obtain Internal Regeneration System (IRS). Allow to come to RT and thaw before opening.
   - IRS recipe (prepared in 100 mM KPO4, pH 8):
     - Glucose-6-phosphate disodium salt (G6P-Na2): 0.333 M (MW 304.098 g/mol)
     - Glucose-6-phosphate dehydrogenase (G6PD): 30 U/mL (ThermoFisher, Cat. J61181-4I)
5. Combine reagents in a conical tube at the following ratios per well:
   - CYP3A4 supersome: 0.02 uL (v/v 0.01)
   - NADP+: 0.04 uL (v/v 0.02)
   - IRS: 0.04 uL (v/v 0.02)
   - Reaction buffer: 1.90 uL (v/v 0.95)
   - **Total: 2.00 uL per well**
6. Invert up and down 10-20x to mix. **Do not vortex.**

### 2. Prepare DBOMF Substrate Master Mix

1. Obtain DBOMF (Setareh Biotech, Cat. 7817; 2 mM stock in ACN, stored at -20C). Allow to come to RT and completely thaw before opening.
2. Combine 1X Reaction Buffer and DBOMF in a conical tube:
   - DBOMF: v/v 0.002
   - Reaction buffer: v/v 0.998
   - **Total: 2.00 uL per well**
3. Vortex for 5-10 sec (5 sec recommended) to mix.

### 3. Prepare Stop Buffer

1. Obtain 0.5 M Tris stop buffer.
2. Aliquot into a conical tube (2 uL/well).

### 4. Load MultiFlo and Dispense CYP Enzyme Master Mix

**Equipment:** Agilent BioTek MultiFlo FX with peri-pump cassette.

1. Load the MultiFlo with the cassette.
2. Set peri-pump to "1 uL".
3. Quick prime peri-pump primary with CYP supersome master mix x2.
4. **Dispense 2 uL** of CYP enzyme master mix into each well at medium speed.

### 5. Preincubation

1. Allow plates to incubate at **RT for 30 minutes** (active preincubation step — enzyme is active with compound, NADP+, and regeneration system).

### 6. Centrifuge

1. Centrifuge plates at **500 rcf for 2 minutes**.
2. Incubate at room temperature for 15 minutes.

### 7. Clean MultiFlo and Prepare for Substrate Dispense

1. Clean the MultiFlo cassette.
2. Load MultiFlo with cassette.
3. Set peri-pump to "1 uL".
4. Quick prime peri-pump primary with substrate master mix x2.

### 8. Dispense Substrate Master Mix

1. **Dispense 2 uL** of DBOMF substrate master mix into each well at medium speed.

### 9. Centrifuge

1. Centrifuge plates at **500 rcf for 2 minutes**.

### 10. Substrate Reaction Incubation

1. Incubate plates at **25C for 30 minutes**.

### 11. Dispense Stop Buffer

1. Transfer plates to MultiFlo.
2. Load MultiFlo with **plastic cassette** for stop buffer.
3. Quick prime peri-pump primary with stop buffer x2.
4. **Dispense 2 uL** of 0.5 M Tris stop buffer into each well at medium speed.

### 12. Centrifuge

1. Centrifuge plates at **500 rcf for 2 minutes**.

### 13. Readout

1. Read plates on **Molecular Devices SpectraMax i3x** plate reader (fluorescence).
   - Cartridge: FI-FLRH, Ex 485 nm / Em 535 nm
   - Integration time: 140 ms
   - Plate type: Revvity Black CulturPlate, 1536-well
   - Read from top, read height 10 mm

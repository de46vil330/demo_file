# Session Log — 2026-03-15

## Overview

This session covered setting up Git and GitHub, building a FizzBuzz TUI application, generating a synthetic CMS-1500 claims dataset, and creating an interactive HTML dashboard to visualize the data.

---

## 1. Git & GitHub Setup

### Git Installation
- Git was already installed: `v2.53.0.windows.1`
- No global config existed — created from scratch

### Global Git Configuration
```bash
git config --global user.name "Daryl Branton"
git config --global user.email "daryl.brayton@gmail.com"
git config --global core.editor "code --wait"
git config --global init.defaultBranch main
git config --global credential.helper manager
```

### Authentication
- Chose **HTTPS with Personal Access Token (PAT)**
- Windows Credential Manager handles token storage after first login

### Repository
- Remote: `https://github.com/de46vil330/demo_file.git`
- Initialized local repo in `demo_folder/`, pushed initial commit

---

## 2. FizzBuzz Application (`main.py`)

### Initial version
- Basic `fizzbuzz(n)` function printing 1–100

### Interactive TUI added
- Loop prompts user for an integer
- Returns `Fizz`, `Buzz`, `FizzBuzz`, or the number
- Handles invalid input gracefully
- Exits on `q` or `quit`

```bash
python main.py
```

**Sample output:**
```
==============================
      FizzBuzz TUI
==============================
Enter a number: 15
  => FizzBuzz

Enter a number: 3
  => Fizz

Enter a number: q
Goodbye!
```

---

## 3. Pull Request Workflow

### PR 1 — `feature/tui-docs`
- Updated README to document the interactive TUI
- Demonstrated the GitHub PR workflow

### PR 2 — `feature/claims-dashboard`
- Updated README to cover full project scope
- Merged documentation for FizzBuzz + CMS-1500 dashboard

---

## 4. CMS-1500 Claims Dataset (`generate_claims.py`)

Generates **100 synthetic CMS-1500 claims** saved to `dat/claims_dataset.csv`.

### Dependencies
```bash
python -m pip install faker
```

### Usage
```bash
python generate_claims.py
```

### Fields generated (55 columns)

| CMS-1500 Box | Fields |
|---|---|
| 1–6 | Insurance type, insured ID, patient name/DOB/sex/address/phone/relationship |
| 9d, 11 | Plan name, group number, insured DOB/sex |
| 14, 17 | Date of illness, referring provider name + NPI |
| 21 | Up to 2 ICD-10 diagnosis codes |
| 23 | Prior authorization number |
| 24 | DOS from/to, place of service, CPT code, modifier, units, charge |
| 25–29 | Tax ID, account number, accept assignment, total charge, amount paid |
| 31–33 | Rendering provider, facility info, billing provider info + NPI |

### CPT codes used

| Code | Description |
|---|---|
| 36415 | Routine venipuncture |
| 93000 | ECG with interpretation |
| 99213 | Office visit, established, low complexity |
| 99214 | Office visit, established, moderate complexity |
| 99215 | Office visit, established, high complexity |
| 99203 | Office visit, new patient, low complexity |
| 99204 | Office visit, new patient, moderate complexity |
| 80053 | Comprehensive metabolic panel |
| 85027 | Complete blood count (CBC) |
| 71046 | Chest X-ray, 2 views |

### ICD-10 codes used
`Z00.00`, `I10`, `E11.9`, `J06.9`, `M54.5`, `F41.1`, `E78.5`, `J18.9`, `N39.0`, `K21.0`

---

## 5. Data Directory & `.gitignore`

- Created `dat/` directory to hold generated data files
- Added `.gitignore` to exclude `dat/` from version control
- Removed `claims_dataset.csv` from git tracking

```
dat/
```

---

## 6. HTML Claims Dashboard (`visualize_claims.py`)

Reads `dat/claims_dataset.csv` and generates `dat/claims_report.html`.

```bash
python visualize_claims.py
```

### Dashboard sections

#### Summary Cards
- Total Claims
- Total Billed
- Total Paid
- Average Charge
- Collection Rate

#### Charts (Chart.js)
- Insurance Type — doughnut
- Place of Service — doughnut
- Top CPT Codes — horizontal bar with full descriptions
- Top ICD-10 Diagnoses — bar

#### Claims Hierarchy (collapsible tree)
- Grouped by: **Relationship → Insurance Type → Claims**
- Relationship order: Self → Spouse → Child → Other
- Expand All / Collapse All controls
- Each claim shows: Account #, Patient, DOS, CPT, Description, ICD-10, Billed, Paid

#### Claims Table
- All 100 claims
- Live search filter
- Clickable column sorting

---

## 7. GitHub CLI Installation

- Installed via winget: `gh v2.88.1`
- Installed to: `C:\Program Files\GitHub CLI\gh.exe`
- Requires `gh auth login` with a PAT to activate

---

## Repository Structure

```
demo_folder/
├── .gitignore              # Excludes dat/
├── README.md               # Project documentation
├── SESSION_LOG.md          # This file
├── main.py                 # FizzBuzz TUI
├── generate_claims.py      # CMS-1500 dataset generator
├── visualize_claims.py     # HTML dashboard generator
└── dat/                    # Git-ignored — generated locally
    ├── claims_dataset.csv
    └── claims_report.html
```

---

## Git Commit History

| Commit | Description |
|---|---|
| `8f946ce` | Initial commit |
| `d6219c9` | Add FizzBuzz application and README |
| `131a0e9` | Add interactive TUI for FizzBuzz |
| `6bd86db` | Add CMS-1500 sample dataset generator and 100 claim records |
| `112e865` | Move dataset to dat/ and add .gitignore to exclude it |
| `237fec8` | Add HTML claims dashboard generator |
| `9603284` | Add collapsible relationship hierarchy to claims dashboard |
| `9be7499` | Update README to document claims dashboard and full project scope |

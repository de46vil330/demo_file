# FizzBuzz & CMS-1500 Claims Dashboard

A FizzBuzz TUI application and CMS-1500 claims data generator with an interactive HTML dashboard, written in Python.

---

## FizzBuzz TUI

### What it does

Prints the FizzBuzz result for any integer you enter:

- **Fizz** — multiples of 3
- **Buzz** — multiples of 5
- **FizzBuzz** — multiples of both 3 and 5
- The number itself — everything else

### Usage

```bash
python main.py
```

### Example

```
==============================
      FizzBuzz TUI
==============================
Enter an integer to get its FizzBuzz result.
Type 'quit' or 'q' to exit.

Enter a number: 15
  => FizzBuzz

Enter a number: 3
  => Fizz

Enter a number: q
Goodbye!
```

---

## CMS-1500 Claims Dataset

Generates 100 synthetic CMS-1500 claims covering all major form fields.

### Usage

```bash
python generate_claims.py   # creates dat/claims_dataset.csv
python visualize_claims.py  # creates dat/claims_report.html
```

### Dashboard features

- Summary cards — total claims, billed, paid, avg charge, collection rate
- Charts — insurance type, place of service, CPT codes, ICD-10 diagnoses
- Collapsible hierarchy — claims grouped by Relationship → Insurance Type
- Searchable, sortable claims table

> **Note:** `dat/` is git-ignored. Data files are generated locally.
